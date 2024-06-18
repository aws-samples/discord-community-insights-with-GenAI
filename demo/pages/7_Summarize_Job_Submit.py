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


st.title("提交总结任务")
analysis_job_id = st.text_input(
    "Enter Job Id👇 (required)",
    placeholder="input job id",
)


if st.button('提交') and analysis_job_id:

    url = domain_url + "/summarize-jobs"

    payload = json.dumps({
      "analysis_job_id": analysis_job_id,
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    st.text(response.text)
    st.success('Submit success!', icon="✅")
else:
    st.error('Please input analysis_job_id', icon="🚨")

st.markdown("示例代码如下：")
code = '''
import requests
import json

url = domain_url + "/summarize-jobs"

payload = json.dumps({
  "analysis_job_id": analysis_job_id,
})
headers = {
  'x-api-key': api_key,
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
'''
st.code(code, language='python')
