import numpy as np
import boto3
import json
import logging
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
from google_play_scraper import search, Sort, reviews
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage,AIMessage

result, continuation_token = reviews(
            'com.nianticlabs.pokemongo',
            lang='en', # defaults to 'en'
            country="us" , # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.NEWEST
            count=100, # defaults to 100
            filter_score_with= 5
        )
print(result)