## discord-community-insights-with-GenAI

## 方案部署

整套解决方案使用AWS CDK进行部署，所以需要在本地具备以下环境：

### 安装依赖

1. 安装nodejs18

```
sudo yum install https://rpm.nodesource.com/pub_18.x/nodistro/repo/nodesource-release-nodistro-1.noarch.rpm -y 
sudo yum install nodejs -y --setopt=nodesource-nodejs.module_hotfixes=1 --nogpgcheck
```

1. 安装&启动docker

```
sudo yum install docker -y
sudo service docker start
sudo chmod 666 /var/run/docker.sock
```

1. 安装git和jq

```
sudo yum install git -y
sudo yum install jq
```

1. 安装aws-cdk

```
sudo npm install -g aws-cdk
sudo npm install --global yarn
```

1. 安装Python3.11（Amazon Linux2023自带Python3.11环境），其他系统可以参考以下安装方式

```
wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz 
tar xzf Python-3.11.8.tgz 
cd Python-3.11.8 
sudo ./configure --enable-optimizations 
```

1. 安装依赖后，依赖信息如下

```
CDK 2.122.0+
nodejs 18+
npm 10+
python 3.11+
git
```

### 开始部署

首先我们需要将示例代码下载到本地

```
git clone https://github.com/aws-samples/discord-community-insights-with-GenAI.git
cd discord-community-insights-with-GenAI/deploy
```

执行生成环境变量脚本，生成相应环境变量，脚本内容如下

```
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
# Webhook Settings DDB表名
DDB_WEBHOOK_SETTINGS_TABLE="webhook-settings"
# Category Settings DDB表名
DDB_CATEGORY_SETTINGS_TABLE="category-settings"
# User Jobs DDB表名
DDB_USER_JOBS_TABLE="user-jobs"

echo "GLUE_JOB_NAME=${GLUE_JOB_NAME}" > .env
echo "GLUE_DISCORD_JOB_NAME=${GLUE_DISCORD_JOB_NAME}" >> .env
echo "GLUE_SUMMARIZE_JOB_NAME=${GLUE_SUMMARIZE_JOB_NAME}" >> .env
echo "LLM_ANALYSIS_TEXT_TABLE_NAME=${LLM_ANALYSIS_TEXT_TABLE_NAME}" >> .env
echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env
echo "RAW_DATA_PREFIX=${RAW_DATA_PREFIX}" >> .env
echo "GLUE_DATABASE=${GLUE_DATABASE}" >> .env
echo "GLUE_TABLE=${GLUE_TABLE}" >> .env
echo "GLUE_SUMMARY_TABLE=${GLUE_SUMMARY_TABLE}" >> .env
echo "DISCORD_SECRET_NAME=${DISCORD_SECRET_NAME}" >> .env
echo "DDB_WEBHOOK_SETTINGS_TABLE=${DDB_WEBHOOK_SETTINGS_TABLE}" >> .env
echo "DDB_CATEGORY_SETTINGS_TABLE=${DDB_CATEGORY_SETTINGS_TABLE}" >> .env
echo "DDB_USER_JOBS_TABLE=${DDB_USER_JOBS_TABLE}" >> .env
```

执行脚本

```
bash ./gen_env.sh 
```

使用 CDK 安装环境

```
npm install
cdk bootstrap
cdk synth
cdk deploy
```

等待几分钟后，方案部署完毕，会有以下输出内容，当然我们也可以在 AWS console 中 CloudFormation 中查看

### Glue Table 创建
```
CREATE EXTERNAL TABLE sentiment_result (
    chat STRING,
    sentiment STRING
)
PARTITIONED BY (
  job_id STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('ignore.malformed.json' = 'true')
LOCATION "s3://<替换上面配置的S3 Bucket名称>/result/"
TBLPROPERTIES (
  "projection.enabled" = "true",
  "projection.job_id.type" = "injected",
  "storage.location.template" = "s3://<替换上面配置的S3 Bucket名称>/result/job_id=${job_id}"
)
```

```
CREATE EXTERNAL TABLE summary_result (
    counts STRING,
    summary STRING
)
PARTITIONED BY (
  job_id STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('ignore.malformed.json' = 'true')
LOCATION "s3://<替换上面配置的S3 Bucket名称>/summary/"
TBLPROPERTIES (
  "projection.enabled" = "true",
  "projection.job_id.type" = "injected",
  "storage.location.template" = "s3://<替换上面配置的S3 Bucket名称>/summary/job_id=${job_id}"
```

### 示例应用程序
#### 启动
```shell
cd discord-community-insights-with-GenAI/demo
streamlit run demo_app.py --server.port 6001
```
#### 默认用户名密码 `seanguo/abc`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Disclaimer
=============================Disclaimer========================================
The sample code or script or other assets are provided as Service Content (in the case that you are using Amazon Web Services China regions) or AWS Content (in the case that you are using Amazon Web Services regions outside Mainland China) (“Assets”) under the Customer Agreement or the relevant written agreement between you and the operator of the relevant Amazon Web Services region (whichever applies). You should not use the Assets in your production accounts, or on production or other critical data. You are responsible for testing, securing, and optimizing the Assets, as appropriate for production grade use based on your specific quality control practices and standards.  Deploying the Assets may incur charges for creating or using Amazon Web Services chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.
示例代码或脚本或其他资料（“资料”）作为您与相关亚马逊云科技区域运营商之间的客户协议或相关书面协议（以适用者为准）下的“服务内容”（如果您使用亚马逊云科技中国区域）或“AWS 内容”（如果您使用中国大陆以外的亚马逊云科技区域）而提供给您。您不应在您的生产账户中使用“资料”，也不应将“资料”用于您的生产或其他关键数据。您负责根据您的特定质量控制实践和标准对“资料”进行测试、采取安全措施和优化，以适合生产级用途。部署“资料”可能会因创建或使用亚马逊云科技收费资源（例如运行Amazon EC2 实例或使用 Amazon S3 存储）而产生费用。
=============================End of disclaimer ===================================