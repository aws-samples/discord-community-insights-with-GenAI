import streamlit as st
import time, requests, json, re
import dotenv
import os

from pathlib import Path

if 'authentication_status' in st.session_state and st.session_state["authentication_status"]:

    script_path = Path(__file__).resolve()
    current_dir = script_path.parent

    dotenv.load_dotenv(os.path.join(current_dir,'../.env'))
    domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
    api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']


    prompt_id = st.text_input(
        "Enter Prompt ID (required)",
        placeholder="input prompt ID",
    )

    if st.button('删除'):
        if prompt_id.strip() == "":
            st.write("Prompt ID cannot be empty！")

        url = f'{domain_url}/prompts/{prompt_id}'

        headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
        }
        response = requests.request("DELETE", url, headers=headers)
        print('Delete:',response)

        if response.status_code == 200:
            st.success('Delete success!', icon="✅")
        else:
            st.error(f'Delete failed with code:{response.status_code} message:{response.content}')
else:
   st.error("please login first")