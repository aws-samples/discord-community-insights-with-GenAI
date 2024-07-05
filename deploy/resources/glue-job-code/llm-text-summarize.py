import numpy as np
import boto3
import json
import sys
import pandas as pd
import os
import re
import time
from langchain_aws import ChatBedrock
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import awswrangler as wr

from awsglue.utils import getResolvedOptions

print("---------------Starting Summarize-----------------")
# 接收参数
args = getResolvedOptions(sys.argv, ['GLUE_DATABASE', 'BUCKET_NAME', 'GLUE_TABLE','ANALYSIS_JOB_ID'])
# print("------------------Default Job Run ID:", args)
job_run_id = args['JOB_RUN_ID']
analysis_job_id = args['ANALYSIS_JOB_ID']
bucket_name = args['BUCKET_NAME']
summary_prefix = 'summary/'
glue_db = args['GLUE_DATABASE']
glue_table = args['GLUE_TABLE']
s3 = boto3.client('s3')
def persist_result_to_s3(key, result):

    print(result)
    # 将序列化后的数组上传到 S3
    s3.put_object(
        Bucket=bucket_name, 
        Key=summary_prefix + 'job_id=' + job_run_id + '/' + key.replace('/', '-') + '-summary.json',  # 文件在 S3 上的路径和文件名
        Body=json.dumps(result)
    )

# 读取数据并应用过滤条件
df = wr.athena.read_sql_query(f'SELECT * FROM sentiment_result where job_id=\'{analysis_job_id}\'', database=glue_db)
print(df)
sentiment_counts = df.groupby('sentiment').size()
print(sentiment_counts)
sentiment_counts_json = sentiment_counts.to_json(orient='index')
print(sentiment_counts_json)


llm_sonnet = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                  model_kwargs={"temperature": 0,
                                "top_k":10,
                                "max_tokens": 1024,
                                "top_p":0.5,
                              })
                              
chat_content = df['chat']
# 使用str.cat()方法将每一行内容添加回车符号并连接在一起
combined_chat = chat_content.str.cat(sep='\n')
print(combined_chat)

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=100
)
split_docs = text_splitter.split_text(combined_chat)
docs = [Document(page_content=doc) for doc in split_docs]

prompt_template = """You are the summarizer of chat records for game players. You need to summarize the chat records within <content>, focusing primarily on opinions regarding in-game mechanisms and game items:
<content>
{text}
</content>
CONCISE SUMMARY:"""
prompt = PromptTemplate.from_template(prompt_template)

refine_template = (
    "You are the summarizer of chat records for game players, your job is to produce a final summary\n"
    "We have provided an existing summary up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original summary in Chinese"
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
final_result = {
    "counts": sentiment_counts_json,
    "summary": result["output_text"]
}

persist_result_to_s3(analysis_job_id, final_result)
print("---------------End Summarize-----------------")
