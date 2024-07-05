import streamlit as st
import time, requests, json

import pandas as pd
import dotenv
import os

from pathlib import Path


if 'authentication_status' in st.session_state and st.session_state["authentication_status"]:
  script_path = Path(__file__).resolve()
  current_dir = script_path.parent
  dotenv.load_dotenv(os.path.join(current_dir,'../.env'))
  domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
  api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

  url = domain_url + "/prompts"
  headers = {
    'x-api-key': api_key
  }

  response = requests.request("GET", url, headers=headers)
  data = json.loads(response.text)
  df = pd.json_normalize(data)

  st.title("提示词列表")

  st.data_editor(
      df.reindex(columns=['id', 'topic', 'prompt_rag', 'prompt_sentiment']),
      hide_index=True,
  )
else:
   st.error("please login first")
