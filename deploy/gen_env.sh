#!/bin/bash

account_id=`aws sts get-caller-identity --query "Account" --output text`
ts=`date +%y-%m-%d-%H-%M-%S`
unique_tag="$account_id-$ts"

# Glue 作业名称
GLUE_JOB_NAME="llm-analysis-text-job"
# Glue Discord 作业名称
GLUE_DISCORD_JOB_NAME="discord-message-collect-job"
# Glue Discord 作业名称
GLUE_SUMMARIZE_JOB_NAME="llm-summarize-job"
# 存储discord token secretname
DISCORD_SECRET_NAME="discord-token"
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
# Glue Catalog中查询S3中总结数据使用表名
GLUE_SUMMARY_TABLE="summary_result"
echo "GLUE_JOB_NAME=${GLUE_JOB_NAME}" > .env
echo "GLUE_DISCORD_JOB_NAME=${GLUE_DISCORD_JOB_NAME}" > .env
echo "GLUE_SUMMARIZE_JOB_NAME=${GLUE_SUMMARIZE_JOB_NAME}" > .env
echo "LLM_ANALYSIS_TEXT_TABLE_NAME=${LLM_ANALYSIS_TEXT_TABLE_NAME}" >> .env
echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env
echo "RAW_DATA_PREFIX=${RAW_DATA_PREFIX}" >> .env
echo "GLUE_DATABASE=${GLUE_DATABASE}" >> .env
echo "GLUE_TABLE=${GLUE_TABLE}" >> .env
echo "GLUE_SUMMARY_TABLE=${GLUE_SUMMARY_TABLE}" >> .env
echo "DISCORD_SECRET_NAME=${DISCORD_SECRET_NAME}" >> .env