import discord
from datetime import datetime, timedelta
import asyncio
import json
import re
import time
import sys
import pytz
import boto3
from botocore.exceptions import ClientError
import logging
from io import StringIO
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

# 设置Discord客户端
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 处理参数信息
args = getResolvedOptions(sys.argv, ['BUCKET_NAME', 'RAW_DATA_PREFIX', 'CHANNEL_ID', 'SECRET_NAME'])
bucket_name = args['BUCKET_NAME']
prefix = args['RAW_DATA_PREFIX']
job_run_id = args['JOB_RUN_ID']
channel_id = args['CHANNEL_ID']
secret_name = args['SECRET_NAME']

print("------------------Current Job Parameters :", job_run_id, channel_id, secret_name)
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d-%H-%M-%S")

def get_discord_token():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return json.loads(get_secret_value_response['SecretString'])

async def get_recent_messages(channel):
    global message_count
    print("Calculating date_from...")
    data_period = int(token_info.get('DATA_PERIOD'))
    date_from = datetime.now() - timedelta(days=data_period)
    print(f"date_from: {date_from}")
    
    all_messages = []
    async for message in channel.history(after=date_from, limit=100):
        all_messages.append(message)
        last_message = message

    while True:
        flag = 0
        async for message in channel.history(after=date_from, before=last_message, limit=100):
            all_messages.append(message)
            last_message = message
            flag += 1
        if flag == 0:
            break

    message_data = [to_json(message) for message in all_messages]
    message_count = len(message_data)
    print(f"Messages count: {message_count}") 
    return message_data

@client.event
async def on_ready():
    global channel
    print(f'{client.user.name} has connected to Discord!')
    try:
        channel = client.get_channel(int(channel_id)) # 此处需要确保channel id为数字
        print(f'channel name : {channel}')
        recent_messages = await get_recent_messages(channel)
        if not recent_messages:
            logging.info("No recent messages found. Exiting program.")
            await client.close()
            sys.exit(0)
        persist_to_s3(channel.name, recent_messages)
    except Exception as e:
        # 记录异常信息
        logging.error(f"Exception occurred: {e}", exc_info=True)
    await client.close()
    print('Discord client closed')

# 将用户信息写入S3中保存
def persist_to_s3(channel_name, messages):

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
            'embeds': [embed.to_dict() for embed in obj.embeds]
            # 'reactions': [reaction.emoji for reaction in obj.reactions]
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

if message_count > 0:
    # -----------------------------Start Analysis Task-------------------------------------------
    result_prefix = 'result/'
    s3 = boto3.client('s3')
    prompt_sentiment = '''
    You are a chat message sentiment classifer
    
    Here is a document you will classify the senetiment
    <doc>
    {content}
    </doc>
    please list all the content then classify the sentiment of each content into [positive,neutral,negative]'
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
    '''
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
    
    #--------------------------------Start Summarize----------------------------------
    print("---------------Starting Summarize-----------------")
    # 接收参数
    args = getResolvedOptions(sys.argv, ['GLUE_DATABASE', 'GLUE_TABLE'])
    # print("------------------Default Job Run ID:", args)
    summary_prefix = 'summary/'
    glue_db = args['GLUE_DATABASE']
    glue_table = args['GLUE_TABLE']
    def persist_summary_to_s3(key, result):
    
        print(result)
        # 将序列化后的数组上传到 S3
        s3.put_object(
            Bucket=bucket_name, 
            Key=summary_prefix + 'job_id=' + job_run_id + '/' + key.replace('/', '-') + '-summary.json',  # 文件在 S3 上的路径和文件名
            Body=json.dumps(result)
        )
    
    # 读取数据并应用过滤条件
    df = wr.athena.read_sql_query(f'SELECT * FROM sentiment_result where job_id=\'{job_run_id}\'', database=glue_db)

    sentiment_counts = df.groupby('sentiment').size()
    sentiment_counts_json = sentiment_counts.to_json(orient='index')
    print(sentiment_counts_json)
                                  
    chat_content = df['chat']
    # 使用str.cat()方法将每一行内容添加回车符号并连接在一起
    combined_chat = chat_content.str.cat(sep='\n')
    
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=100
    )
    split_docs = text_splitter.split_text(combined_chat)
    docs = [Document(page_content=doc) for doc in split_docs]
    
    llm_summarize = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                      model_kwargs={"temperature": 0,
                                    "top_k":10,
                                    "max_tokens": 1024,
                                    "top_p":0.5
                                   })
    
    prompt_template = """You are the summarizer of chat records for game players. You need to summarize the chat records within <content> in Chinese, focusing primarily on opinions regarding in-game mechanisms and game items.
    You need to provide a summary based on three dimensions: positive feedback, negative feedback, and player suggestions. Additionally, you should provide typical player chat for each dimension.
    <content>
    {text}
    </content>
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)
    
    refine_template = (
        "You are the summarizer of chat records for game players, your job is to produce a final summary in Chinese\n"
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
        llm=llm_summarize,
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
    
    persist_summary_to_s3(job_run_id, final_result)
    print("---------------End Summarize-----------------")
else:
    print("!!!!!!!!!!!No message need to be Summarize!!!!!!!!!!!!!")

def persist_job_info():

    job_info_prefix = 'user-jobs/'
    tz = pytz.timezone('Asia/Shanghai')
    # 获取当前时间,并转换为UTC+8时区时间
    now = datetime.now(tz)
    milliseconds = int(now.timestamp() * 1000)
    # 格式化时间字符串
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    job_info = {
        "channel_id": channel_id,
        "channel_name": channel.name,
        "message_count": message_count,
        "job_run_id": job_run_id,
        "run_time": time_str,
        "timestamp": milliseconds,
    }
    bucket.put_object(
        Key=job_info_prefix + 'username=' + token_info.get("USER_NAME") + '/' + str(milliseconds) + '.json',  # 文件在 S3 上的路径和文件名
        Body=json.dumps(job_info)
    )

persist_job_info()