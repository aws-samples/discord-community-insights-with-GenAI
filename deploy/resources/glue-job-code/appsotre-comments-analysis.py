import numpy as np
import boto3
import json
import logging
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import hashlib
import hmac
import requests
import base64
from google_play_scraper import search, Sort, reviews
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage,AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder,HumanMessagePromptTemplate
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain_core.prompts import PromptTemplate
import awswrangler as wr
from awsglue.utils import getResolvedOptions

print("---------------Starting Analysis-----------------")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# 接收参数
args = getResolvedOptions(sys.argv, ['BUCKET_NAME', 'RAW_DATA_PREFIX', 'PROMPT_TEMPLATE_TABLE','USER_JOBS_TABLE', 'USER_JOB_ID', 'DDB_WEBHOOK_SETTINGS_TABLE'])
print("------------------Default Job Run ID:", args)
job_run_id = args['JOB_RUN_ID']

user_job_id = args['USER_JOB_ID']

bucket_name = args['BUCKET_NAME']
prefix = args['RAW_DATA_PREFIX']
prompt_table_name = args['PROMPT_TEMPLATE_TABLE']
webhook_table_name = args['DDB_WEBHOOK_SETTINGS_TABLE']
user_jobs_table_name = args['USER_JOBS_TABLE']
result_prefix = 'result/'

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# Get Job Information
partition_key_name = 'id'
partition_key_value = user_job_id

job_info = dynamodb.query(
    TableName=user_jobs_table_name,
    KeyConditionExpression=f'{partition_key_name} = :val',
    ExpressionAttributeValues={
        ':val': {'S': partition_key_value}
    }
)
if len(job_info['Items']) == 0:
    print("************Wrong JOB ID**************:",user_job_id)
    
app_name = job_info['Items'][0]['app_name']['S']
store_name = job_info['Items'][0]['store_name']['S']
country_name = job_info['Items'][0]['country_name']['S']
prompt_id = job_info['Items'][0]['prompt_id']['S']
webhook_id = job_info['Items'][0]['webhook_id']['S']

# Get prompt info
partition_key_name = 'id'
partition_key_value = prompt_id

# 查询提示词记录
response = dynamodb.query(
    TableName=prompt_table_name,
    KeyConditionExpression=f'{partition_key_name} = :val',
    ExpressionAttributeValues={
        ':val': {'S': partition_key_value}
    }
)

if len(response['Items']) == 0:
    print("************Wrong PROMPT ID**************:",prompt_id)

categories = response['Items'][0]['categories']['S']
prompt_rag = response['Items'][0]['prompt_rag']['S']
prompt_sentiment = response['Items'][0]['prompt_sentiment']['S']

print('categories:',categories)
print('prompt_rag:',prompt_rag)
print('prompt_sentiment:',prompt_sentiment)

# 查询Webhook信息
webhook_partition_key_name = 'id'
webhook_partition_key_value = webhook_id

webhook_response = dynamodb.query(
    TableName=webhook_table_name,
    KeyConditionExpression=f'{webhook_partition_key_name} = :val',
    ExpressionAttributeValues={
        ':val': {'S': webhook_partition_key_value}
    }
)

if len(webhook_response['Items']) == 0:
    print("************Wrong Webhook ID**************:",webhook_id)
else:
    webhook_url = webhook_response['Items'][0]['url']['S']
    webhook_secret = webhook_response['Items'][0]['secret']['S']

class CustOuputParser(BaseOutputParser[str]):
    
    def extract(self, content: str) -> tuple[str, str]:
        pattern = r'"(.*?)" \[(.*?)\]'
        matches = re.findall(pattern, content)
        if matches:
            return [(text, category) for text, category in matches]
    
    def parse(self, text: str) -> str:
        results = self.extract(text)
        if results:
            output = []
            for text, category in results:
                output.append(json.dumps({"chat": text, "category": category}, ensure_ascii=False))
            return "\n".join(output)
        else:
            return ''
    
    @property
    def _type(self) -> str:
        return "cust_output_parser"

class FeiShu():
    webhook_url = ''
    secret = ''
    def __init__(self,webhook_url,secret):
        self.webhook_url = webhook_url
        self.secret = secret
    
    def gen_sign(self, secret, timestamp):# 拼接时间戳以及签名校验
        
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        # 使用 HMAC-SHA256 进行加密
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        # 对结果进行 base64 编码
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    def send_message(self, text):
        timestamp = int(datetime.now().timestamp())
        sign = self.gen_sign(self.secret, timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "text",
            "content": {"text": text},
        }

        resp = requests.post(self.webhook_url, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result.get("code") != 0:
            print(f"发送失败：{result['msg']}")
            return
        print("消息发送成功")


# get google appid before get app reviews.
def get_google_app_id(app_name:str):
    print(app_name)
    result = search(
        app_name,
        lang="en",  # defaults to 'en'
        country="us",  # defaults to 'us'
        n_hits=1  # defaults to 30 (= Google's maximum)
    )
    print(len(result))
    return result

def generate_text(bedrock_client, model_id, input_text):
    logger.info("Generating text with model %s", model_id)
   # Create the initial message from the user input.
    messages = [{
        "role": "user",
        "content": [{"text": input_text}]
    }]

    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages
    )

    output_message = response['output']['message']
    messages.append(output_message)
    stop_reason = response['stopReason']

    # print the final response from the model.
    for content in output_message['content']:
        print(json.dumps(content, indent=4))

def get_google_play_app_review(app_id:str,country:str,rank:int = -1,page:int=1 ):
    """Tool to found Google App Store App reviews by app id ,country ,rank and page"""
    try:
        
        filter_score = None
        if rank > 0 and rank <6:
            filter_score = rank
        print(f"{country=}")
        result, continuation_token = reviews(
            app_id,
            lang='en', # defaults to 'en'
            country="us" if country=="" else country , # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.NEWEST
            count=100 # defaults to 100
        )
        
        if continuation_token:
            print(f'Have continuation token: {continuation_token}')

        # if len(result) > 0:
        #     process_app_review_with_llm(result)
        # save_review(app_id, result)
        # with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
        #     json.dump(result, file, cls=DateTimeEncoder,ensure_ascii=False, indent=4)

        return [{"username":review["userName"],"content":review["content"],"score":review["score"]} for review in result]
    except Exception as e:
        print(e)
        return []

def save_review_data(app_id:str,type:str,file_name:str, data):
    prefix = f"appstore/{type}/job_id={job_run_id}/{file_name}"
    # 将序列化后的数组上传到 S3
    s3.put_object(
        Bucket=bucket_name, 
        Key=prefix,  # 文件在 S3 上的路径和文件名
        Body='\n'.join(data)
    )

raw_reviews = []
if store_name == 'Google Play':
    app_name_arr = get_google_app_id(app_name)
    if len(app_name_arr) == 0:
        print(f"invalid app_name: {app_name} in {store_name}")
    else:
        app_name = app_name_arr[0]
        print(f"app_name is {app_name} in {store_name}")
        raw_reviews = get_google_play_app_review(app_name['appId'],'us')
else:
    print(f"not support for current store {store_name}")

prompt_rag = ChatPromptTemplate.from_template(prompt_rag)
llm_sonnet = ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                  model_kwargs={"temperature": 0,
                                "top_k":10,
                                "max_tokens": 1024,
                                "system": "You must always output response in Chinese",
                                "top_p":0.1,
                                # "stop_sequences":['</response>']
                               })
output_parser  = CustOuputParser()
rag_chain = prompt_rag | llm_sonnet | output_parser
text = "\n".join(str(re) for re in raw_reviews)
answer = rag_chain.invoke({'context':text})
print(answer)
all_result = []
if answer:
    all_result += answer.split('\n')
save_review_data(app_name,"category", "category.json",all_result);
        
logger.info("========================Start Summary By Category=======================")
glue_db = 'llm_text_db'
glue_table = 'category_result'
category_list = categories.split(",")

# 初始化飞书实例
message_channel = FeiShu(webhook_url=webhook_url, secret=webhook_secret)
ss_result = []
for cate in category_list:

    # 读取数据并应用过滤条件
    df = wr.athena.read_sql_query(f'SELECT * FROM category_result where job_id=\'{job_run_id}\' and category like \'%{cate}%\'', database=glue_db)
    print(f"Category: {cate} Counts: {len(df)}")
                                  
    chat_content = df['chat']
    # 使用str.cat()方法将每一行内容添加回车符号并连接在一起
    combined_chat = chat_content.str.cat(sep='\n')
    
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=100
    )
    split_docs = text_splitter.split_text(combined_chat)
    docs = [Document(page_content=doc) for doc in split_docs]
    prompt = PromptTemplate.from_template(prompt_sentiment)
    refine_template = (
        "You are the summarizer of application reviews in Application Store for game players, your job is to produce a final summary in Chinese\n"
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Given the new context, refine the original summary"
        "If the context isn't useful, return the original summary."
    )
    refine_prompt = PromptTemplate.from_template(refine_template)
    chain = load_summarize_chain(
        llm=llm_sonnet,
        chain_type="refine",
        question_prompt=prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=True,
        input_key="input_documents",
        output_key="output_text",
    )
    result = chain.invoke({"input_documents": docs}, return_only_outputs=True)
    print(result["output_text"])
    ss_result.append(json.dumps({'category': cate, 'summary': result["output_text"]}))
    message_channel.send_message(result["output_text"])
save_review_data(app_name,"summary", "summary.json",ss_result);