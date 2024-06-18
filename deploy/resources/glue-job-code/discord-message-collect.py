import discord
from datetime import datetime, timedelta
import asyncio
import json
import re
import time
import sys
import boto3
from botocore.exceptions import ClientError
import logging
from io import StringIO
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage,AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder,HumanMessagePromptTemplate
from langchain_core.output_parsers.base import BaseOutputParser
from awsglue.utils import getResolvedOptions

# 设置Discord客户端
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 处理参数信息
args = getResolvedOptions(sys.argv, ['BUCKET_NAME', 'RAW_DATA_PREFIX'])
bucket_name = args['BUCKET_NAME']
prefix = args['RAW_DATA_PREFIX']
job_run_id = args['JOB_RUN_ID']
print("------------------Default Job Run ID:", job_run_id)
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d-%H-%M-%S")

def get_discord_token():
    secret_name = "discord-token"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return json.loads(get_secret_value_response['SecretString'])

async def get_recent_messages(channel):
    print("Calculating one_week_ago...")
    one_week_ago = datetime.now() - timedelta(days=7)
    print(f"one_week_ago: {one_week_ago}")
    messages = [message async for message in channel.history(after=one_week_ago)]
    message_data = [to_json(message) for message in messages]
    print(f"Messages count: {len(message_data)}")
    return message_data

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    try:
        channel = client.get_channel(token_info.get('CHANNEL_ID')) # 此处需要确保channel id为数字
        print(f'channel name : {channel}')
        recent_messages = await get_recent_messages(channel)
        persist_to_s3(channel.name, recent_messages)
    except Exception as e:
        # 记录异常信息
        logging.error(f"Exception occurred: {e}", exc_info=True)
    await client.close()
    print('Discord client closed')

# 将用户信息写入S3中保存
def persist_to_s3(channel_name, messages):
    print(messages)
    global prefix_key
    output_buffer = StringIO()

    # 遍历每个 JSON 对象并写入到 StringIO 对象中
    for item in messages:
        output_buffer.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 获取 StringIO 对象的值
    output_data = output_buffer.getvalue()
    
    # 获取存储桶对象
    bucket = s3.Bucket(bucket_name)
    # 将序列化后的数组上传到 S3
    prefix_key = prefix + 'Discord/' + channel_name + '/' + formatted_time +'.json'
    bucket.put_object(
        Key=prefix_key,  # 文件在 S3 上的路径和文件名
        Body=output_data
    )

def to_json(obj):
    if isinstance(obj, discord.User):
        return {
            'id': obj.id,
            'name': obj.name,
            'global_name': obj.global_name,
            'is_bot': obj.bot
        }
    elif isinstance(obj, discord.Message):
        return {
            'id': obj.id,
            'content': obj.content,
            'author': to_json(obj.author),
            'channel_id': obj.channel.id,
            'guild_id': obj.guild.id if obj.guild else None,
            'timestamp': obj.created_at.isoformat(),
            'edited_at': obj.edited_at.isoformat() if obj.edited_at else None,
            'attachments': [attachment.url for attachment in obj.attachments],
            'embeds': [embed.to_dict() for embed in obj.embeds],
            'reactions': [reaction.emoji for reaction in obj.reactions]
        }
    elif isinstance(obj, discord.TextChannel):
        return {
            'id': obj.id,
            'name': obj.name,
            'guild_id': obj.guild.id,
            'category_id': obj.category_id,
            'position': obj.position
        }
    elif isinstance(obj, discord.Member):
        return {
            'id': obj.id,
            'name': obj.name
        }
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

async def run_once():
    global token_info
    token_info = get_discord_token()
    print(token_info)
    print(type(token_info))
    await client.start(token_info.get('TOKEN'))

asyncio.run(run_once())


# -----------------------------Start Analysis Task-------------------------------------------
prompt_id = 'bfdff416-7f14-42b0-aff5-cb7f0333d1c2'
table_name = 'prompt-template'
result_prefix = 'result/'

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# 设置提示词信息
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

class CustOuputParser(BaseOutputParser[str]):

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

prompt_sentiment = ChatPromptTemplate.from_template(prompt_sentiment)
llm_sonnet = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                  model_kwargs={"temperature": 0,
                                "top_k":10,
                                "max_tokens": 1024,
                                "top_p":0.5,
                                # "stop_sequences":['</response>']
                               })
output_parser  = CustOuputParser()
sentiment_chain = prompt_sentiment | llm_sonnet | output_parser

def split_into_chunks(arr, n):
    chunks = []
    for i in range(0, len(arr), n):
        chunks.append(arr[i:i+n])
    return chunks

def llm_analysis(key, chunks):
    all_result = []
    for i,chunk in enumerate(chunks):
        t1 = time.time()
        print(f'--------chunk idx:{i}-------')
        text =  "\n".join(chunk)
        answer = sentiment_chain.invoke({'content':text})
        if answer:
            all_result += answer.split('\n')
    persist_result_to_s3(key, all_result)

def persist_result_to_s3(key, results):

    print(results)
    file_content = '\n'.join(results)
    # 将序列化后的数组上传到 S3
    s3.put_object(
        Bucket=bucket_name, 
        Key=result_prefix + 'job_id=' + job_run_id + '/' + key.replace('/', '-') + '-result.json',  # 文件在 S3 上的路径和文件名
        Body=file_content
    )

filtered_msg = []
obj = s3.get_object(Bucket=bucket_name, Key=prefix_key)
# 读取对象内容
content = obj['Body'].read().decode('utf-8')
# 按行分割内容
lines = content.split('\n')
# 遍历每一行并解析JSON对象
for line in lines:
    if line.strip():  # 跳过空行
        data = json.loads(line)
        # 处理JSON对象
        if data.get('content') and data.get('content') != '':
            filtered_msg.append(data.get('content'))

# 将聊天记录分成chunk            
chunks = split_into_chunks(filtered_msg,200)
print(f'Number of chunks: {len(chunks)}')
llm_analysis(formatted_time,chunks)