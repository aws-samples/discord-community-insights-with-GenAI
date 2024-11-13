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

  url = domain_url + "/categories"
  headers = {
    'x-api-key': api_key
  }

  name = st.text_input(
      "Enter Category Name",
      key='name'
  )
  categories = st.text_area(
      "Enter Categories",
      key='categories'
  )

  if st.button('提交'):

      if name.strip() == "":
          st.write("Name cannot be empty！")

      if categories.strip() == "":
          st.write("Categories cannot be empty！")

      url = domain_url + "/categories"

      headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      response = requests.request("GET", url, headers=headers).json()
      print('GET:',response)
      
      payload_dict = {
        "name": name,
        "categories": categories
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
