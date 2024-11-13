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

  def getAllPrompts():
      url = domain_url + "/prompts"
      headers = {
       'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      response = requests.request("GET", url, headers=headers).json()
      print('GET:',response)
      return response
  
  def getAllWebhooks():
      url = domain_url + "/webhooks"
      headers = {
       'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      response = requests.request("GET", url, headers=headers).json()
      print('GET:',response)
      return response
  webhooks = getAllWebhooks()
  prompts = getAllPrompts()
  names = [data['name'] for data in prompts]
  print(names)
  webhook_names = [data['name'] for data in webhooks]

  selected_name_index = st.selectbox("=======>选择提示词<=======", names)

  appStores = ['Google Play','App Store']
  selected_store_index = st.selectbox("=======>选择应用商店<=======", appStores)

  countries = ['us','jp']
  selected_country_index = st.selectbox("=======>选择国家<=======", countries)
  # 根据选定的索引显示相应的 JSON 数据
  app_name = st.text_input(
      "Enter App Name👇 (required)",
      key="app_name",
      placeholder="App Name",
      # value=prompt_rag_sample,
  )

  name = st.text_input(
      "Enter Job Name👇 (required)",
      key="job_name",
      placeholder="Job Name",
      # value=prompt_rag_sample,
  )

  crons = st.text_input(
      "Enter Crons👇 (required)",
      key="crons",
      placeholder="Like: cron(24 05 * * ? *)",
      # value=prompt_rag_sample,
  )

  selected_webhook_name_index = st.selectbox("=======>选择发送渠道<=======", webhook_names)
  
  try:
    selected_name = next(data for data in prompts if data['name'] == selected_name_index)
  except StopIteration:
    selected_name = None
  
  try:
    selected_webhook_name = next(data for data in webhooks if data['name'] == selected_webhook_name_index)
  except StopIteration:
    selected_webhook_name = None


  if st.button('提交'):
      url = domain_url + "/myjobs"
      headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      response = requests.request("GET", url, headers=headers).json()
      print('GET:',response)
      
      payload_dict = {
        "prompt_id": selected_name['id'],
        "crons": crons,
        "app_name": app_name,
        "store_name": selected_store_index,
        "country_name": selected_country_index,
        "webhook_id": selected_webhook_name['id'],
        "name": name
      }
      payload = json.dumps(payload_dict)

      headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
      }
      print(payload)
      response = requests.request("POST", url, headers=headers, data=payload)

      if response.status_code == 200:
          st.success('Submit success!', icon="✅")
      else:
          st.error(f'Submit failed with code:{response.status_code} message:{response.content}')
else:
   st.error("please login first")
