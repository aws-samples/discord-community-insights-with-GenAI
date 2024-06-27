import streamlit as st
from PIL import Image
import dotenv
import os
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError) 

script_path = Path(__file__).resolve()
current_dir = script_path.parent
dotenv.load_dotenv(os.path.join(current_dir,'.env'))
st.set_page_config(
    page_title="舆情AI洞察系统",
    page_icon="👋",
)

st.write("# Welcome to 舆情AI洞察系统 👋")
# 需要根据Cloudformation中的内容来设定URL
if 'domain_url' not in st.session_state:
    st.session_state.domain_url = os.environ['domain_url']
# 需要根据Cloudformation中的内容来设定API KEY
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ['apikeys']

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    st.write(f'Welcome *{st.session_state["name"]}*')
    img = Image.open(os.path.join(current_dir,'images/arch.png'))
    st.image(img)
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
