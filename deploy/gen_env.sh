#!/bin/bash

account_id=`aws sts get-caller-identity --query "Account" --output text`
ts=`date +%y-%m-%d-%H-%M-%S`
unique_tag="$account_id-$ts"


GLUE_JOB_NAME="llm-analysis-text-job"
LLM_ANALYSIS_TEXT_TABLE_NAME="prompt-template"
S3_BUCKET_NAME="${unique_tag}-llm-analysis-text"
RAW_DATA_PREFIX="raw-data/"
GLUE_DATABASE="llm_text_db"
GLUE_TABLE="sentiment_result"
domain_url="placeholder please change as after the output of cdk deploy result"
apikeys="placeholder"
echo "GLUE_JOB_NAME=${GLUE_JOB_NAME}" > .env
echo "LLM_ANALYSIS_TEXT_TABLE_NAME=${LLM_ANALYSIS_TEXT_TABLE_NAME}" >> .env
echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env
echo "RAW_DATA_PREFIX=${RAW_DATA_PREFIX}" >> .env
echo "GLUE_DATABASE=${GLUE_DATABASE}" >> .env
echo "GLUE_TABLE=${GLUE_TABLE}" >> .env
echo "domain_url=${domain_url}" >> .env
echo "apikeys=${apikeys}" >> .env

