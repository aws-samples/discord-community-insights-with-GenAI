import streamlit as st
import time, requests, json

import pandas as pd
import dotenv
import os

from pathlib import Path
if 'authentication_status' in st.session_state and st.session_state["authentication_status"]:
    username = st.session_state["username"]
    script_path = Path(__file__).resolve()
    current_dir = script_path.parent
    dotenv.load_dotenv(os.path.join(current_dir,'../.env'))
    domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
    api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

    channel_name = st.text_input(
        "Channel Name",
        placeholder="input channel name",
    )
    url = domain_url + "/user-jobs"
    if st.button('实时查询'):
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "username": username,
        }
        if channel_name != '':
            payload['channel_name'] = channel_name

        response = json.loads(requests.request("Post", url, headers=headers, data = json.dumps(payload)).text)
        # 提取列名
        columns = [col_info["Name"] for col_info in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]
        # 提取行数据
        rows_data = [row["Data"] for row in response["ResultSet"]["Rows"] if row.get("Data")]

        # 将每行数据转换为字典，并添加到列表中
        df = pd.DataFrame(columns=columns)

        # 遍历查询结果，并将值添加到DataFrame中
        for row in rows_data[1:]:
            values = [item.get('VarCharValue', '') for item in row]
            row_data = {}
            for i in range(len(columns)):
                row_data[columns[i]] = values[i]
            df = df.append(row_data, ignore_index=True)

        st.data_editor(
            df,
            hide_index=True,
        )
        st.success('Query success!', icon="✅")
else:
   st.error("please login first")