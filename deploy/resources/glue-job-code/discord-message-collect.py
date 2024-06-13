import discord
from datetime import datetime, timedelta
import asyncio
import json
import sys
import boto3
from botocore.exceptions import ClientError
import logging
from io import StringIO
from awsglue.utils import getResolvedOptions

# 设置Discord客户端
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 处理参数信息
args = getResolvedOptions(sys.argv, ['BUCKET_NAME', 'RAW_DATA_PREFIX'])
bucket_name = args['BUCKET_NAME']
prefix = args['RAW_DATA_PREFIX']
print("------------------Default Job Run ID:", args)
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
    
    output_buffer = StringIO()

    # 遍历每个 JSON 对象并写入到 StringIO 对象中
    for item in messages:
        output_buffer.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 获取 StringIO 对象的值
    output_data = output_buffer.getvalue()
    
    # 获取存储桶对象
    bucket = s3.Bucket(bucket_name)
    # 将序列化后的数组上传到 S3
    bucket.put_object(
        Key=prefix + 'Discord/' + channel_name + '/' + formatted_time +'.json',  # 文件在 S3 上的路径和文件名
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