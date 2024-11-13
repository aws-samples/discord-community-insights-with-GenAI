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

  name = st.text_input(
      "Enter Webhook Name",
      key='name'
  )
  webhook_url = st.text_area(
      "Enter Webhook URL",
      key='webhook_url'
  )

  secret = st.text_area(
      "Enter Secret",
      key='secret'
  )

  if st.button('提交'):

      if name.strip() == "":
          st.write("Name cannot be empty！")

      if webhook_url.strip() == "":
          st.write("Webhook URL cannot be empty！")

      if secret.strip() == "":
          st.write("Secret cannot be empty！")

      url = domain_url + "/webhooks"

      headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      response = requests.request("POST", url, headers=headers).json()
      print('GET:',response)
      
      payload_dict = {
        "name": name,
        "url": webhook_url,
        "secret": secret
      }

      payload = json.dumps(payload_dict)

      headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
      }

      response = requests.request("POST", url, headers=headers, data=payload)

      if response.status_code == 200:
          st.success('Submit success!', icon="✅")
      else:
          st.error(f'Submit failed with code:{response.status_code} message:{response.content}')
else:
   st.error("please login first")
