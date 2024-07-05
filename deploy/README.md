# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

### Create Glue Analysis Table
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
### Create Glue Summary Table
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
)
```
