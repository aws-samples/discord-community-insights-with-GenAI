import numpy as np
import boto3
import json
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


print("---------------Starting Analysis-----------------")

s3 = boto3.resource('s3')
bucket_name = 'jiangyu-rag'
prefix = 'raw-data/'
result_prefix = 'result/'

# 获取存储桶对象
bucket = s3.Bucket(bucket_name)

llm_sonnet = BedrockChat(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                  model_kwargs={"temperature": 0,
                                "top_k":10,
                                "max_tokens": 1024,
                                "top_p":0.5,
                                # "stop_sequences":['</response>']
                               })
template_extract = \
"""You are an expert research assistant, tasked with identifying player sentiments regarding certain in-game items, neutral NPCs, and game market activities.

Here is a document you will analyze
<doc>
{context}
</doc>

Here is a task:
First, find the quotes from the document that are most relevant to {topic}, and then print them in numbered order. Quotes should be relatively short.
If there are no relevant quotes, write "No relevant quotes" instead.
please enclose your analysis results in xml tag <response>.

for example:
<response>
1. "拍卖行多香"
2. "我拍到好东西了"
3. "拍卖行太差劲了"
4. "auction sucks"
5. "拍卖行有人发包"
</response>

Skip the preamble, go straight into the answer.
"""

template_sentiment = \
"""You are a chat message sentiment classifer

Here is a document you will classify the senetiment
<doc>
{relevant_info}
</doc>


please list all the content if it is relevant to {topic} and classify the sentiment of each content into [positive,neutral,negative]'

Please follow below requirements:
1. You will strictly be based on the document in <doc>.
2. please enclose your analysis results in xml tag <sentiment>.

for example:
<sentiment>
1. "拍卖行多香" [positive]
2. "我拍到好东西了" [positive]
3. "拍卖行太差劲了" [negative]
4. "auction sucks" [negative]
5. "拍卖行有人发包" [neutral]
</sentiment>

Skip the preamble, go straight into the answer.

"""
prompt_extract = ChatPromptTemplate.from_template(template_extract)
prompt_sentiment = ChatPromptTemplate.from_template(template_sentiment)

# 提取有价值聊天记录
def extract_value_data(lines):
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
        Key=result_prefix+key+'.json',  # 文件在 S3 上的路径和文件名
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
        pattern = r'"(.*?)" \[(.*?)\]'
        matches = re.findall(pattern, content)
        if matches:
            return [(text, sentiment) for text, sentiment in matches]

    def parse(self, text: str) -> str:
        results = self.extract(text)
        output = []
        for text, sentiment in results:
            output.append(json.dumps({"chat": text, "sentiment": sentiment}, ensure_ascii=False))
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
    for i,chunk in enumerate(chunks[:2]):
        t1 = time.time()
        print(f'--------chunk idx:{i}-------')
        text =  "\n".join(chunk)
        answer = full_chain.invoke({'topic':"auction house",
                           'context':text})
        if answer:
            all_result += answer.split('\n')
    persist_to_s3(key, all_result)



# 遍历目录中的所有文件
for obj in bucket.objects.filter(Prefix=prefix):
    if obj.key.endswith('/'):
        continue
    # 读取文件内容
    body = obj.get()['Body'].read().decode('utf-8')
    print(f'======>String Analysis File: {obj.key}')
    # 将文件内容转换为字符串列表
    lines = body.split('\n')
    # 获取行数
    num_lines = len(lines)
    print(f'Total lines: {num_lines}')

    # 获取有价值聊天记录
    value_lines = extract_value_data(lines)
    print(f'Value lines: {len(value_lines)}')

    # 切分文件
    chunks = split_into_chunks(value_lines,2000)
    print(f'Number of chunks: {len(chunks)}')
    llm_analysis(obj.key,chunks)

print("---------------End Analysis-----------------")
