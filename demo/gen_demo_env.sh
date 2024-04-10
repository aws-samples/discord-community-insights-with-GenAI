#!/bin/bash
# Api Gateway 暴露的domain URL，需要在CDK 部署完毕后进行配置
domain_url="https://xxxx.execute-api.us-east-1.amazonaws.com/prod/"
# 调用Api Gateway 暴露的domain URL API key，需要在CDK 部署完毕后进行配置
apikeys=""
echo "domain_url=${domain_url}" >> .env
echo "apikeys=${apikeys}" >> .env
