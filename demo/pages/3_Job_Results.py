import streamlit as st
import time, requests, json

domain_url = st.session_state.domain_url
api_key = st.session_state.api_key

def submit_job():
    print("查看结果")

job_id = st.text_input(
    "Enter Job Id👇 (required)",
    placeholder="input job id",
)

sql = st.text_area(
    "Customize Sql(Optional)",
    "Just like: select count(1), sentiment from sentiment_result group by sentiment",
)

if st.button('实时查询'):
    if job_id.strip() == "":
        st.write("Job Id 不能为空")

    url = domain_url + "/jobs/results?job_id=" + job_id
    payload = json.dumps({
      "sql": sql
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
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

