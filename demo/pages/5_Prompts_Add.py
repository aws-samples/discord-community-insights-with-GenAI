import streamlit as st
import time, requests, json, re
import dotenv
import os

from pathlib import Path

script_path = Path(__file__).resolve()
current_dir = script_path.parent
env_dir = script_path.parent.parent.parent

dotenv.load_dotenv(os.path.join(env_dir,'deploy/.env'))
domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

prompt_rag_sample = '''
You are an expert research assistant, tasked with identifying player sentiments regarding certain in-game items, neutral NPCs, and game market activities.

Here is a document you will analyze
<doc>
{context}
</doc>

Here is a task:
First, find the quotes from the document that are most relevant to {topic}, and then print them in numbered order. Quotes should be relatively short.
If there are no relevant quotes, write "No relevant quotes" instead.
please enclose your analysis results in xml tag <response>.

for example:
<response>
$SAMPLE$
</response>

Skip the preamble, go straight into the answer.
'''
prompt_sentiment_sample = '''
You are a chat message sentiment classifer

Here is a document you will classify the senetiment
<doc>
{relevant_info}
</doc>
please list all the content if it is relevant to {topic} and classify the sentiment of each content into [positive,neutral,negative]'
Please follow below requirements:
1. You will strictly be based on the document in <doc>.
2. please enclose your analysis results in xml tag <sentiment>.

for example:
<sentiment>
$SAMPLE$
</sentiment>

Skip the preamble, go straight into the answer.
'''

def few_shot_callback():
    sample_sentiment_text = st.session_state.sample_text
    original_texts = sample_sentiment_text.split("\n")
    processed_texts = []
    for text in original_texts:
        processed_text = re.sub(r'\s*\[.*?\]\s*$', '', text)
        processed_texts.append(processed_text)
    st.session_state.prompt_sentiment = prompt_sentiment_sample.replace('$SAMPLE$', sample_sentiment_text)
    st.session_state.prompt_rag = prompt_rag_sample.replace('$SAMPLE$', '\n'.join(processed_texts))



topic = st.text_input(
    "Enter Topic👇 (required)",
    placeholder="input topic name,like '拍卖行'",
)

prompt_rag = st.text_area(
    "Enter Prompt Rag👇 (required)",
    key="prompt_rag",
    height=12,
    placeholder="Prompt RAG, using to extract relavent information from raw data",
    # value=prompt_rag_sample,
)

prompt_sentiment = st.text_area(
    "Enter Prompt Sentiment👇 (required)",
    key="prompt_sentiment",
    height=12,
    placeholder="Prompt Sentiment, using to analysis sentiment infromation from extracted data",
    # value=prompt_sentiment_sample,
)

sample_text = st.text_area(
    "Enter Samples👇 (optional)",
    placeholder=
    """
    1. "拍卖行多香" [positive]
    2. "我拍到好东西了" [positive]
    3. "拍卖行太差劲了" [negative]
    4. "auction sucks" [negative]
    5. "拍卖行有人发包" [neutral]""",
    key='sample_text',
    on_change=few_shot_callback
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
    print('GET:',response)
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

    if response.status_code == 200:
        st.success('Submit success!', icon="✅")
    else:
        st.error(f'Submit failed with code:{response.status_code} message:{response.content}')  
    

st.markdown("### 提示词样例如下，其中{context} , {relevant_info} 和 {topic}请不要动")
st.markdown("### Prompt RAG")
code = '''
You are an expert research assistant, tasked with identifying player sentiments regarding certain in-game items, neutral NPCs, and game market activities.

Here is a document you will analyze
<doc>
{context}
</doc>

Here is a task:
First, find the quotes from the document that are most relevant to {topic}, and then print them in numbered order. Quotes should be relatively short.
If there are no relevant quotes, write "No relevant quotes" instead.
please enclose your analysis results in xml tag <response>.

for example:
<response>
1. "拍卖行多香"
2. "我拍到好东西了"
3. "拍卖行太差劲了"
4. "auction sucks"
5. "拍卖行有人发包"
</response>

Skip the preamble, go straight into the answer.
'''
st.code(code, language='python')
st.markdown("### Prompt Sentiment")
code = '''
You are a chat message sentiment classifer

Here is a document you will classify the senetiment
<doc>
{relevant_info}
</doc>
please list all the content if it is relevant to {topic} and classify the sentiment of each content into [positive,neutral,negative]'
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
st.code(code, language='python')



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
