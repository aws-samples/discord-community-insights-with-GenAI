import streamlit as st
import time, requests, json

import pandas as pd
import dotenv
import os

from pathlib import Path

script_path = Path(__file__).resolve()
current_dir = script_path.parent
dotenv.load_dotenv(os.path.join(current_dir,'../.env'))
domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

url = domain_url + "/discord-1click-jobs"
payload = ""
headers = {
  'x-api-key': api_key
}
# st.set_page_config(page_title="分析任务列表", layout="wide")
st.title("Discord任务列表")
response = requests.request("GET", url, headers=headers, data=payload)
if response.status_code == 200:
    data= json.loads(response.text)
    df = pd.json_normalize(data['jobRuns'])
    if df.empty:
        st.write("暂无分析任务")
    else:
        df['result_link'] = '/result?job_id=' + df['Id']

    st.data_editor(
        df,
        hide_index=True,
    )