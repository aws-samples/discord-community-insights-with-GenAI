import streamlit as st
import pandas as pd
import time, requests, json
import dotenv
import os
import matplotlib.pyplot as plt
from pathlib import Path

script_path = Path(__file__).resolve()
current_dir = script_path.parent
dotenv.load_dotenv(os.path.join(current_dir,'../.env'))
domain_url = st.session_state.domain_url  if 'domain_url' in st.session_state else os.environ['domain_url']
api_key = st.session_state.api_key  if 'api_key' in st.session_state else os.environ['apikeys']

def submit_job():
    print("查看结果")

job_id = st.text_input(
    "Enter Summarize Job Id👇 (required)",
    placeholder="input job id",
)

if st.button('实时查询'):
    if job_id.strip() == "":
        st.write("Job Id 不能为空")

    url = domain_url + "/summarize-jobs?job_id=" + job_id

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


    # 创建饼图
    

    # 遍历查询结果，并将值添加到DataFrame中
    for row in rows_data[1:]:
        values = [item.get('VarCharValue', '') for item in row]
        row_data = {}
        for i in range(len(columns)):
            row_data[columns[i]] = values[i]
        df = df.append(row_data, ignore_index=True)

    counts_dict = df['counts'].apply(json.loads)
    # 从字典中获取键值对
    labels = counts_dict.apply(lambda x: list(x.keys()))
    sizes = counts_dict.apply(lambda x: list(x.values()))
    fig, ax = plt.subplots()
    ax.pie(sizes[0], labels=labels[0], autopct='%1.1f%%')
    ax.axis('equal')  # 设置x,y轴刻度相等,使饼图为正圆形

    # 在 Streamlit 中显示
    st.pyplot(fig)

    summary_values = df['summary'].values
    st.markdown(summary_values[0])

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
payload = json.dumps({
    "job_id": job_id,
    "sql": sql
})

response = json.loads(requests.request("Post", url, headers=headers, data = payload).text)
'''
st.code(code, language='python')
