import streamlit as st

st.set_page_config(
    page_title="舆情分析系统",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a demo above.")

if 'domain_url' not in st.session_state:
    st.session_state.domain_url = "https://wifrpdv052.execute-api.us-east-1.amazonaws.com/prod"
    
if 'api_key' not in st.session_state:
    st.session_state.api_key = "hTJvdee2uXphpeUHeXE824vePhFX1LR8qpQPMbE8"


st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)
