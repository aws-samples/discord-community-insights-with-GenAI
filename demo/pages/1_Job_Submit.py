import streamlit as st
import time, requests, json

domain_url = st.session_state.domain_url
api_key = st.session_state.api_key

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

prompts = get_prompts()

topics = [data['topic'] for data in prompts]
print(prompts)
st.title("提交分析任务")
selected_data_index = st.selectbox("=======>选择提示词<=======", topics)

# 根据选定的索引显示相应的 JSON 数据
selected_json = next(data for data in prompts if data['topic'] == selected_data_index)

# 将选定的 JSON 数据显示在页面上
st.text(selected_json['id'])

if st.button('提交'):

    url = domain_url + "/jobs"

    payload = json.dumps({
      "prompt_id": selected_json['id']
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    st.text(response.text)
    st.success('Submit success!', icon="✅")

st.markdown("示例代码如下：")
code = '''
import requests
import json

url = "https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod//jobs"

payload = json.dumps({
  "prompt_id": "248367b6-b36a-47fe-81c8-038579fb6b96"
})
headers = {
  'x-api-key': 'xxxxxxxxxxxxx',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
'''
st.code(code, language='python')

    