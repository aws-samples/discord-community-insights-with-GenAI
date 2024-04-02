import streamlit as st
import time, requests, json

domain_url = st.session_state.domain_url
api_key = st.session_state.api_key
topic = st.text_input(
    "Enter Topic👇 (required)",
    placeholder="input topic name,like '拍卖行'",
)

prompt_rag = st.text_area(
    "Enter Prompt Rag👇 (required)",
    placeholder="Prompt RAG, using to extract relavent information from raw data",
)

prompt_sentiment = st.text_area(
    "Enter Prompt Sentiment👇 (required)",
    placeholder="Prompt Sentiment, using to analysis sentiment infromation from extracted data",
)

if st.button('提交'):
    if topic.strip() == "":
        st.write("Topic cannot be empty！")

    if prompt_rag.strip() == "":
        st.write("Prompt RAG cannot be empty！")

    if prompt_sentiment.strip() == "":
        st.write("Prompt sentiment cannot be empty！")

    url = domain_url + "/prompts"

    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = json.loads(requests.request("GET", url, headers=headers).text)

    payload = json.dumps({
      "topic": topic,
      "prompt_rag": prompt_rag,
      "prompt_sentiment": prompt_sentiment
    })
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    st.success('Submit success!', icon="✅")

st.markdown("示例代码如下：")
code = '''
url = domain_url + "/prompts"

headers = {
  'x-api-key': api_key,
  'Content-Type': 'application/json'
}
response = json.loads(requests.request("GET", url, headers=headers).text)

payload = json.dumps({
  "topic": topic,
  "prompt_rag": prompt_rag,
  "prompt_sentiment": prompt_sentiment
})
headers = {
  'x-api-key': api_key,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
'''
st.code(code, language='python')
