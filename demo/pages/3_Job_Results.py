import streamlit as st
import pandas as pd
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
    placeholder="Just like: select count(1), sentiment from sentiment_result group by sentiment",
)

if st.button('实时查询'):
    if job_id.strip() == "":
        st.write("Job Id 不能为空")

    url = domain_url + "/jobs/results?job_id=" + job_id

    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = json.loads(requests.request("GET", url, headers=headers).text)

    # 提取列名
    columns = [col_info["Name"] for col_info in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

    # 提取行数据
    rows_data = [row["Data"] for row in response["ResultSet"]["Rows"] if row.get("Data")]

    # 将每行数据转换为字典，并添加到列表中
    df = pd.DataFrame(columns=columns)

    # 遍历查询结果，并将值添加到DataFrame中
    for row in rows_data[1:]:
        values = [item.get('VarCharValue', '') for item in row]
        chat_sentiment_dict = eval(values[0])
        row_data = {}
        for i in range(len(columns)):
            if i < len(values)-1:
                row_data[columns[i]] = chat_sentiment_dict.get(columns[i], '')
            else:
                row_data[columns[i]] = values[i]
        df = df.append(row_data, ignore_index=True)

    st.data_editor(
        df,
        hide_index=True,
    )
    st.success('Query success!', icon="✅")





st.markdown("示例代码如下：")
code = '''
import requests
import pandas
import json

url = domain_url + "/jobs/results?job_id=" + job_id

headers = {
  'x-api-key': api_key,
  'Content-Type': 'application/json'
}
response = json.loads(requests.request("GET", url, headers=headers).text)

# 提取列名
columns = [col_info["Name"] for col_info in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

# 提取行数据
rows_data = [row["Data"] for row in response["ResultSet"]["Rows"] if row.get("Data")]

# 将每行数据转换为字典，并添加到列表中
df = pd.DataFrame(columns=columns)

# 遍历查询结果，并将值添加到DataFrame中
for row in rows_data[1:]:
    values = [item.get('VarCharValue', '') for item in row]
    chat_sentiment_dict = eval(values[0])
    row_data = {}
    for i in range(len(columns)):
        if i < len(values)-1:
            row_data[columns[i]] = chat_sentiment_dict.get(columns[i], '')
        else:
            row_data[columns[i]] = values[i]
    df = df.append(row_data, ignore_index=True)

st.data_editor(
    df,
    hide_index=True,
)
'''
st.code(code, language='python')
