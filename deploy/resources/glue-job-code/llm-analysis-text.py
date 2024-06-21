import numpy as np
import boto3
import json
import sys
import pandas as pd
import re
import time
import pickle
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage,AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder,HumanMessagePromptTemplate
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.runnables import RunnableLambda
from operator import itemgetter
from awsglue.utils import getResolvedOptions

print("---------------Starting Analysis-----------------")

# 接收参数
args = getResolvedOptions(sys.argv, ['PROMPT_ID', 'BUCKET_NAME', 'RAW_DATA_PREFIX', 'PROMPT_TEMPLATE_TABLE'])
print("------------------Default Job Run ID:", args)
job_run_id = args['JOB_RUN_ID']
prompt_id = args['PROMPT_ID']
bucket_name = args['BUCKET_NAME']
prefix = args['RAW_DATA_PREFIX']
table_name = args['PROMPT_TEMPLATE_TABLE']
result_prefix = 'result/'

s3 = boto3.resource('s3')
dynamodb = boto3.client('dynamodb')
bucket = s3.Bucket(bucket_name)

partition_key_name = 'id'
partition_key_value = prompt_id

# 查询提示词记录
response = dynamodb.query(
    TableName=table_name,
    KeyConditionExpression=f'{partition_key_name} = :val',
    ExpressionAttributeValues={
        ':val': {'S': partition_key_value}
    }
)

if len(response['Items']) == 0:
    print("************Wrong PROMPT ID**************:",prompt_id)

topic = response['Items'][0]['topic']['S']
prompt_rag = response['Items'][0]['prompt_rag']['S']
prompt_sentiment = response['Items'][0]['prompt_sentiment']['S']

print('topic:',topic)
print('prompt_rag:',prompt_rag)
print('prompt_sentiment:',prompt_sentiment)
prompt_extract = ChatPromptTemplate.from_template(prompt_rag)
prompt_sentiment = ChatPromptTemplate.from_template(prompt_sentiment)

llm_sonnet = BedrockChat(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                  model_kwargs={"temperature": 0,
                                "top_k":10,
                                "max_tokens": 1024,
                                "top_p":0.5,
                                # "stop_sequences":['</response>']
                               })

# 提取有价值聊天记录
def extract_value_data_from_text(lines):
    extracted_data = []
    # 提取聊天的正则表达式模式
    pattern = r'"m":"(.*?)"'
    # 遍历每一行
    for line in lines:
        match = re.search(pattern, line)
        if match:
            text = match.group(1)
            if not text.startswith('link'):
                extracted_data.append(text)
    return extracted_data

def extract_value_data_from_csv(lines):
    extracted_data = []
    # 遍历每一行
    for line in lines:
        if not line.startswith('link'):
            extracted_data.append(line)
    return extracted_data

# 切分文件
def split_into_chunks(arr, n):
    chunks = []
    for i in range(0, len(arr), n):
        chunks.append(arr[i:i+n])
    return chunks

def persist_to_s3(key, results):

    print(results)
    file_content = '\n'.join(results)
    # 获取存储桶对象
    bucket = s3.Bucket(bucket_name)

    # 将序列化后的数组上传到 S3
    bucket.put_object(
        Key=result_prefix + 'job_id=' + job_run_id + '/' + key.replace('/', '-') +'.json',  # 文件在 S3 上的路径和文件名
        Body=file_content
    )

class CustOuputParser(BaseOutputParser[str]):

    def extract(self,content:str) -> str:
        pattern = r"<response>(.*?)</response>"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1)
            text = text.replace('[','(').replace(']',')') ##避免跟sentiment的格式冲突
            return text
        else:
            return 'No relevant quotes'

    def parse(self, text: str) -> str:
        cleaned_text = self.extract(text)
        return cleaned_text

    @property
    def _type(self) -> str:
        return "cust_output_parser"


class CustOuputParser2(BaseOutputParser[str]):

    def extract(self, content: str) -> tuple[str, str]:
        pattern = r'\d\.\s(.*?)\[(.*?)\]'
        matches = re.findall(pattern, content)
        if matches:
            return [(text, sentiment) for text, sentiment in matches]

    def parse(self, text: str) -> str:
        results = self.extract(text)
        print(results)
        output = []
        for text, sentiment in results:
            output.append(json.dumps({"chat": text.replace("\"",""), "sentiment": sentiment}, ensure_ascii=False))
        return "\n".join(output)

    @property
    def _type(self) -> str:
        return "cust_output_parser"


output_parser = CustOuputParser()
output2_parser  = CustOuputParser2()
chain_1 = prompt_extract | llm_sonnet | output_parser
chain_2 = prompt_sentiment | llm_sonnet| output2_parser

def route(info):
    if not 'no relevant quotes' in info['relevant_info'].lower():
        return chain_2

full_chain = ({'relevant_info':chain_1,'topic':itemgetter('topic')})| RunnableLambda(route)


def llm_analysis(key, chunks):
    all_result = []
    for i,chunk in enumerate(chunks):
        t1 = time.time()
        print(f'--------chunk idx:{i}-------')
        text =  "\n".join(chunk)
        answer = full_chain.invoke({'topic':topic, 'context':text})
        if answer:
            all_result += answer.split('\n')
    persist_to_s3(key, all_result)


# 遍历目录中的所有文件
for obj in bucket.objects.filter(Prefix=prefix):
    if obj.key.endswith('/'):
        continue
    # 读取文件内容

    if obj.key.endswith('.csv'):
        print(f'======>String Analysis File: {obj.key}')
        df = pd.read_csv(obj.get()['Body'])
        lines = df['_col6'].to_list()
        # 获取行数
        num_lines = len(lines)
        print(f'Total lines: {num_lines}')

        value_lines = extract_value_data_from_csv(lines)
        print(f'Value lines: {len(value_lines)}')
    else:
        body = obj.get()['Body'].read().decode('utf-8')
        # 将文件内容转换为字符串列表
        lines = body.split('\n')
        # 获取行数
        num_lines = len(lines)
        print(f'Total lines: {num_lines}')

        # 获取有价值聊天记录
        value_lines = extract_value_data_from_text(lines)
        print(f'Value lines: {len(value_lines)}')

    # 切分文件
    chunks = split_into_chunks(value_lines,2000)
    print(f'Number of chunks: {len(chunks)}')
    llm_analysis(obj.key,chunks)

print("---------------End Analysis-----------------")
