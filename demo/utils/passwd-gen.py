import streamlit as st
import dotenv
import sys
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

all_args = sys.argv
first_arg = sys.argv[1]
print(first_arg)
print(Hasher([first_arg]).generate()[0])