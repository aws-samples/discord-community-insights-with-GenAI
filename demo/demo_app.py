import streamlit as st
from PIL import Image
import dotenv
import os

import os
from pathlib import Path

script_path = Path(__file__).resolve()
current_dir = script_path.parent
env_dir = script_path.parent.parent

dotenv.load_dotenv(os.path.join(env_dir,'deploy/.env'))
st.set_page_config(
    page_title="舆情分析系统",
    page_icon="👋",
)

st.write("# Welcome to 舆情分析系统 👋")

# 需要根据Cloudformation中的内容来设定URL
if 'domain_url' not in st.session_state:
    st.session_state.domain_url = os.environ['domain_url']
# 需要根据Cloudformation中的内容来设定API KEY
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ['apikeys']


st.markdown(
    """
    ### Architecture Overview
"""
)

img = Image.open(os.path.join(current_dir,'images/arch.png'))
st.image(img)
