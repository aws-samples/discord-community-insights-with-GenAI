#!/bin/bash

account_id=`aws sts get-caller-identity --query "Account" --output text`
ts=`date +%y-%m-%d-%H-%M-%S`
unique_tag="$account_id-$ts"

# Glue 作业名称
GLUE_JOB_NAME="llm-analysis-text-job"
# DynamoDB中存储prompt的表名
LLM_ANALYSIS_TEXT_TABLE_NAME="prompt-template"
# 存储原始数据以及分析结果的S3名称
S3_BUCKET_NAME="llm-analysis-text-${unique_tag}"
# S3中原始数据Prefix的名称
RAW_DATA_PREFIX="raw-data/"
# Glue Catalog中DB名称
GLUE_DATABASE="llm_text_db"
# Glue Catalog中查询S3中分析数据使用表名
GLUE_TABLE="sentiment_result"
# Api Gateway 暴露的domain URL，需要在CDK 部署完毕后进行配置
domain_url="https://wifrpdv052.execute-api.us-east-1.amazonaws.com/prod/"
# 调用Api Gateway 暴露的domain URL API key，需要在CDK 部署完毕后进行配置
apikeys="hTJvdee2uXphpeUHeXE824vePhFX1LR8qpQPMbE8"
echo "GLUE_JOB_NAME=${GLUE_JOB_NAME}" > .env
echo "LLM_ANALYSIS_TEXT_TABLE_NAME=${LLM_ANALYSIS_TEXT_TABLE_NAME}" >> .env
echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env
echo "RAW_DATA_PREFIX=${RAW_DATA_PREFIX}" >> .env
echo "GLUE_DATABASE=${GLUE_DATABASE}" >> .env
echo "GLUE_TABLE=${GLUE_TABLE}" >> .env
echo "domain_url=${domain_url}" >> .env
echo "apikeys=${apikeys}" >> .env

