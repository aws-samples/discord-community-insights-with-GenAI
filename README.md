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