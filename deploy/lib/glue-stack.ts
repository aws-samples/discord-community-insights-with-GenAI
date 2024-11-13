import * as glue from '@aws-cdk/aws-glue-alpha';
import * as cdk from 'aws-cdk-lib';
import {NestedStack, CfnOutput, NestedStackProps} from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";
import { Secret, SecretStringGenerator } from 'aws-cdk-lib/aws-secretsmanager';
import * as path from "path";
import {DeployConstant} from "./deploy-constants";



export interface GlueStackProps extends NestedStackProps {
    texts3: cdk.aws_s3.Bucket,
}

export class GlueStack extends NestedStack {

    public readonly secret:Secret
    jobArn = '';
    jobName = '';
    discordJobArn = '';
    discordJobName = '';
    /**
     *
     * @param {Construct} scope
     * @param {string} id
     * @param {StackProps=} props
     */
    constructor(scope: Construct, id: string, props: GlueStackProps) {
        super(scope, id, props);

        // const database = new glue.Database(this, 'llm-text-db2',{databaseName: DeployConstant.GLUE_DATABASE})
        // const table = new glue.S3Table(this, 'llm-text-table2', {
        //     database: database,
        //     tableName: 'sentiment_result',
        //     columns: [
        //         { name: 'chat', type: glue.Schema.STRING },
        //         { name: 'sentiment', type: glue.Schema.STRING },
        //     ],
        //     dataFormat: glue.DataFormat.JSON,
        //     partitionKeys: [{ name: 'job_id', type: glue.Schema.STRING }],
        //     bucket: props.texts3, // 替换为您的 S3 Bucket 名称
        //     enablePartitionFiltering: true,
        //     s3Prefix: '/result',
        //     storageParameters: [
        //         glue.StorageParameter.custom('projection.enabled', 'true'),
        //         glue.StorageParameter.custom('projection.job_id.type', 'injected'),
        //         glue.StorageParameter.custom('storage.location.template', 's3://' + props.texts3.bucketName + '/result/job_id=${job_id}'),
        //     ]
        // })

        const scriptPath = path.resolve(__dirname, '../resources/glue-job-code/llm-analysis-text.py');

        const job = new glue.Job(this, 'llm-analysis-text',{
            jobName: DeployConstant.GLUE_JOB_NAME,
            executable: glue.JobExecutable.pythonEtl({
                glueVersion: glue.GlueVersion.V4_0,
                pythonVersion: glue.PythonVersion.THREE,
                script: glue.Code.fromAsset(scriptPath),
            }),
            maxConcurrentRuns:200,
            maxRetries:0,
            defaultArguments:{
                '--BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                '--RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
                '--PROMPT_TEMPLATE_TABLE': DeployConstant.LLM_ANALYSIS_TEXT_TABLE_NAME,
                '--additional-python-modules': 'langchain==0.1.12,langchain-community==0.0.28,boto3>=1.34.64,botocore>=1.34.64'
            }
        })
        job.role.addToPrincipalPolicy(
            new iam.PolicyStatement({
                actions: [
                    "s3:List*",
                    "s3:Put*",
                    "s3:Get*",
                    "dynamodb:*",
                    "bedrock:*",
                ],
                effect: iam.Effect.ALLOW,
                resources: ['*'],
            })
        )
        this.jobArn = job.jobArn;
        this.jobName = job.jobName;

        /** Discord collect data job */

        this.secret = new Secret(this, 'MySecret', {
            secretName: DeployConstant.DISCORD_SECRET_NAME,
            description: 'Discord Token',
            generateSecretString: {
                secretStringTemplate: JSON.stringify({ CHANNEL_ID: 123,  
                    TOKEN: ''}),
                generateStringKey: 'password',
              },
          });

        const discordScriptPath = path.resolve(__dirname, '../resources/glue-job-code/discord-message-collect.py');

        const discordJob = new glue.Job(this, 'glue-discord-job',{
            jobName: DeployConstant.GLUE_DISCORD_JOB_NAME,
            executable: glue.JobExecutable.pythonEtl({
                glueVersion: glue.GlueVersion.V4_0,
                pythonVersion: glue.PythonVersion.THREE,
                script: glue.Code.fromAsset(discordScriptPath),
            }),
            maxConcurrentRuns:200,
            maxRetries:0,
            defaultArguments:{
                '--BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                '--SECRET_NAME': DeployConstant.DISCORD_SECRET_NAME,
                '--RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
                '--additional-python-modules': 'discord.py==2.3.2,langchain-aws==0.1.6,langchain-community==0.2.4'
            }
        })
        discordJob.role.addToPrincipalPolicy(
            new iam.PolicyStatement({
                actions: [
                    "s3:List*",
                    "s3:Put*",
                    "s3:Get*",
                    "secretsmanager:GetSecretValue",
                    "dynamodb:*",
                    "bedrock:*",
                ],
                effect: iam.Effect.ALLOW,
                resources: ['*'],
            })
        )
        this.discordJobArn = discordJob.jobArn;
        this.discordJobName = discordJob.jobName;


        const summaryJobScriptPath = path.resolve(__dirname, '../resources/glue-job-code/llm-text-summarize.py');

        const summaryJob = new glue.Job(this, 'glue-summarize-job',{
            jobName: DeployConstant.GLUE_SUMMARIZE_JOB_NAME,
            executable: glue.JobExecutable.pythonEtl({
                glueVersion: glue.GlueVersion.V4_0,
                pythonVersion: glue.PythonVersion.THREE,
                script: glue.Code.fromAsset(summaryJobScriptPath),
            }),
            maxConcurrentRuns:200,
            maxRetries:0,
            defaultArguments:{
                '--BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                '--GLUE_DATABASE': DeployConstant.GLUE_DATABASE,
                '--GLUE_TABLE': DeployConstant.GLUE_TABLE,
                '--additional-python-modules': 'langchain-aws==0.1.6,langchain-community==0.2.4,awswrangler==3.8.0,tiktoken==0.7.0'
            }
        })
        summaryJob.role.addToPrincipalPolicy(
            new iam.PolicyStatement({
                actions: [
                    "s3:*",
                    "athena:*",
                    "dynamodb:*",
                    "bedrock:*",
                ],
                effect: iam.Effect.ALLOW,
                resources: ['*'],
            })
        )

        // Discord one click Job
        const discord1clickScriptPath = path.resolve(__dirname, '../resources/glue-job-code/discord-one-click.py');

        const discordOneclickJob = new glue.Job(this, 'discord-1click-job',{
            jobName: DeployConstant.GLUE_DISCORD_1CLICK_JOB_NAME,
            executable: glue.JobExecutable.pythonEtl({
                glueVersion: glue.GlueVersion.V4_0,
                pythonVersion: glue.PythonVersion.THREE,
                script: glue.Code.fromAsset(discord1clickScriptPath),
            }),
            maxConcurrentRuns:200,
            maxRetries:0,
            defaultArguments:{
                '--BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                '--GLUE_DATABASE': DeployConstant.GLUE_DATABASE,
                '--GLUE_TABLE': DeployConstant.GLUE_TABLE,
                '--SECRET_NAME': DeployConstant.DISCORD_SECRET_NAME,
                '--RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
                '--additional-python-modules': 'discord.py==2.3.2,langchain-aws==0.1.6,langchain-community==0.2.4,awswrangler==3.8.0,tiktoken==0.7.0'
            }
        })
        discordOneclickJob.role.addToPrincipalPolicy(
            new iam.PolicyStatement({
                actions: [
                    "s3:*",
                    "athena:*",
                    "dynamodb:*",
                    "secretsmanager:GetSecretValue",
                    "bedrock:*",
                ],
                effect: iam.Effect.ALLOW,
                resources: ['*'],
            })
        )


        // AppStore Job
        const appstoreScriptPath = path.resolve(__dirname, '../resources/glue-job-code/appsotre-comments-analysis.py');

        const appstoreJob = new glue.Job(this, 'appstore-job',{
            jobName: DeployConstant.GLUE_APPSTORE_JOB_NAME,
            executable: glue.JobExecutable.pythonEtl({
                glueVersion: glue.GlueVersion.V4_0,
                pythonVersion: glue.PythonVersion.THREE,
                script: glue.Code.fromAsset(appstoreScriptPath),
            }),
            maxConcurrentRuns:200,
            maxRetries:0,
            defaultArguments:{
                '--BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                '--GLUE_DATABASE': DeployConstant.GLUE_DATABASE,
                '--GLUE_TABLE': DeployConstant.GLUE_TABLE,
                '--RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
                '--PROMPT_TEMPLATE_TABLE': DeployConstant.LLM_ANALYSIS_TEXT_TABLE_NAME,
                '--DDB_WEBHOOK_SETTINGS_TABLE': DeployConstant.DDB_WEBHOOK_SETTINGS_TABLE,
                '--USER_JOBS_TABLE': DeployConstant.DDB_USER_JOBS_TABLE,
                '--additional-python-modules': 'langchain-aws==0.1.6,langchain-community==0.2.4,awswrangler==3.8.0,requests==2.32.3,bs4==0.0.2,google-play-scraper==1.2.7,tiktoken==0.7.0'
            }
        })
        appstoreJob.role.addToPrincipalPolicy(
            new iam.PolicyStatement({
                actions: [
                    "s3:*",
                    "athena:*",
                    "dynamodb:*",
                    "bedrock:*",
                ],
                effect: iam.Effect.ALLOW,
                resources: ['*'],
            })
        )

    }

}
