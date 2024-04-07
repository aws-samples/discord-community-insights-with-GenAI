import streamlit as st
import time, requests, json
import dotenv
import os

from pathlib import Path

script_path = Path(__file__).resolve()
current_dir = script_path.parent
dotenv.load_dotenv(os.path.join(current_dir,'../.env'))

domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

def submit_job():
    url = domain_url + "/jobs"
    payload = json.dumps({
      "prompt_id": "248367b6-b36a-47fe-81c8-038579fb6b96"
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def get_prompts():
    prompts_url = domain_url + "/prompts"
    prompts_headers = {
      'x-api-key': api_key
    }

    prompts_response = requests.request("GET", prompts_url, headers=prompts_headers, data={})
    return json.loads(prompts_response.text)


def get_chatdata():
    data_url = domain_url + "/chat-data"
    headers = {
      'x-api-key': api_key
    }
    response = requests.request("GET", data_url, headers=headers, data={})
    return json.loads(response.text)

prompts = get_prompts()
chatdata = get_chatdata()

topics = [data['topic'] for data in prompts]
st.title("提交分析任务")
selected_topic_index = st.selectbox("=======>选择提示词<=======", topics)
selected_data_index = st.selectbox("=======>选择源数据<=======", chatdata)
st.text(f"chatdata:{chatdata}")
# 根据选定的索引显示相应的 JSON 数据
try:
  selected_topic = next(data for data in prompts if data['topic'] == selected_topic_index)
except StopIteration:
  selected_topic = None

try:
  selected_data = next(data for data in chatdata if data == selected_data_index)
except StopIteration:
  selected_data = None


if st.button('提交') and selected_topic and selected_data:

    url = domain_url + "/jobs"

    payload = json.dumps({
      "prompt_id": selected_topic['id'],
      "prefix": selected_data
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    st.text(response.text)
    st.success('Submit success!', icon="✅")
else:
    st.error('Please select a topic and chat data!', icon="🚨")

st.markdown("示例代码如下：")
code = '''
import requests
import json

url = domain_url + "/jobs"

    payload = json.dumps({
      "prompt_id": selected_topic['id'],
      "prefix": selected_data
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
'''
st.code(code, language='python')
