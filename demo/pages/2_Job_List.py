import streamlit as st
import time, requests, json

import pandas as pd

domain_url = st.session_state.domain_url
api_key = st.session_state.api_key

url = domain_url + "/jobs"
payload = ""
headers = {
  'x-api-key': api_key
}

response = requests.request("GET", url, headers=headers, data=payload)
data = json.loads(response.text)
df = pd.json_normalize(data['jobRuns'])
st.set_page_config(page_title="分析任务列表", layout="wide")
st.title("分析任务列表")

df['result_link'] = '/result?job_id=' + df['Id']

st.data_editor(
    df
    hide_index=True,
)

st.markdown("示例代码如下：")
code = '''
url = "https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod/jobs"

payload = ""
headers = {
  'x-api-key': 'xxxxxxxxxxxxxxxxxxx'
}

response = requests.request("GET", url, headers=headers, data=payload)
'''
st.code(code, language='python')
