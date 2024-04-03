import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="舆情分析系统",
    page_icon="👋",
)

st.write("# Welcome to 舆情分析系统 👋")

st.sidebar.success("Select a demo above.")

if 'domain_url' not in st.session_state:
    st.session_state.domain_url = "https://wifrpdv052.execute-api.us-east-1.amazonaws.com/prod"

if 'api_key' not in st.session_state:
    st.session_state.api_key = "hTJvdee2uXphpeUHeXE824vePhFX1LR8qpQPMbE8"


st.markdown(
    """
    ### Architecture Overview
"""
)

img = Image.open('./images/arch.png')
st.image(img)
