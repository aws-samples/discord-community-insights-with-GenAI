import * as cdk from 'aws-cdk-lib';
import {Duration, NestedStack, NestedStackProps} from 'aws-cdk-lib';
import * as lambdanodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";
import {DeployConstant} from "./deploy-constants";
import { Secret } from 'aws-cdk-lib/aws-secretsmanager';

export interface LambdaStackProps extends NestedStackProps {
    secret: Secret,
}

export class LambdaStack extends NestedStack {

    public readonly submitJobFunction: lambda.IFunction;
    public readonly promptTemplateFunction: lambda.IFunction;
    public readonly getGlueJobFunction: lambda.IFunction;
    public readonly getAthenaResultsFunction: lambda.IFunction;
    public readonly getRawDataDirectoriesFunction: lambda.IFunction;
    public readonly submitSummarizeJobFunction: lambda.IFunction;
    public readonly getSummaryResultsFunction: lambda.IFunction;
    public readonly getSummaryJobsFunction: lambda.IFunction;
    public readonly modifyDiscordSettingsFunction: lambda.IFunction;
    public readonly getDiscord1ClickJobFunction: lambda.IFunction;
    public readonly startDiscord1ClickJobFunction: lambda.IFunction;

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        const glueJobLambdaRole = new iam.Role(this, 'ApigLambdaRole', {
            roleName: `submit-job-lambda--${cdk.Stack.of(this).region}`,
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAthenaFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('SecretsManagerReadWrite'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonEventBridgeFullAccess'),
            ],
            inlinePolicies: {
                'GlueFullAccess': new iam.PolicyDocument({
                    assignSids: true,
                    statements: [
                        new iam.PolicyStatement({
                            effect: iam.Effect.ALLOW,
                            actions: [
                                'glue:*'
                            ],
                            resources: [
                                '*'
                            ]
                        })
                    ]
                })
            }
        });

        const promptTemplateLambdaRole = new iam.Role(this, 'PromptTemplateLambdaRole', {
            roleName: `prompt-template-lambda--${cdk.Stack.of(this).region}`,
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonDynamoDBFullAccess'),
            ],
        });

        const functionSettings : lambdanodejs.NodejsFunctionProps = {
            handler: 'handler',
            runtime: lambda.Runtime.NODEJS_LATEST,
            memorySize: 1024,
            timeout: cdk.Duration.seconds(60),
            architecture: cdk.aws_lambda.Architecture.X86_64,
            logRetention: cdk.aws_logs.RetentionDays.ONE_WEEK
        }

        this.submitJobFunction = new lambdanodejs.NodejsFunction(this, 'SubmitGlueJob', {
            functionName: 'submit-glue-job-func',
            entry: './resources/lambda/submit-analysis-glue-job.ts',
            role: glueJobLambdaRole,
            environment: {
                'GLUE_JOB_NAME': DeployConstant.GLUE_JOB_NAME,
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                'RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
                'PROMPT_TEMPLATE_TABLE': DeployConstant.LLM_ANALYSIS_TEXT_TABLE_NAME,
            },
            ...functionSettings
        });

        this.promptTemplateFunction = new lambdanodejs.NodejsFunction(this, 'PromptTemplateFunction', {
            functionName: 'prompt-template-func',
            entry: './resources/lambda/prompt-template-function.ts',
            role: promptTemplateLambdaRole,
            environment: {
                'TABLE_NAME': DeployConstant.LLM_ANALYSIS_TEXT_TABLE_NAME,
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
            },
            ...functionSettings
        });

        this.getGlueJobFunction = new lambdanodejs.NodejsFunction(this, 'GetGlueFunction', {
            functionName: 'get-glue-job-func',
            entry: './resources/lambda/get-glue-job-list.ts',
            role: glueJobLambdaRole,
            environment: {
                'GLUE_JOB_NAME': DeployConstant.GLUE_JOB_NAME,
            },
            ...functionSettings
        });

        this.getAthenaResultsFunction = new lambdanodejs.NodejsFunction(this, 'GetAthenaResultsFunc', {
            functionName: 'get-athena-results-func',
            entry: './resources/lambda/athena-job-results.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                'TABLE_NAME': DeployConstant.GLUE_TABLE,
                'DATABASE_NAME': DeployConstant.GLUE_DATABASE,
            },
            ...functionSettings
        });

        this.getRawDataDirectoriesFunction = new lambdanodejs.NodejsFunction(this, 'GetRawDataDirectories', {
            functionName: 'get-raw-data-directories-func',
            entry: './resources/lambda/get-s3-data-directories.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                'RAW_DATA_PREFIX': DeployConstant.RAW_DATA_PREFIX,
            },
            ...functionSettings
        });

        this.submitSummarizeJobFunction = new lambdanodejs.NodejsFunction(this, 'SubmitSummarizeJob', {
            functionName: 'submit-summarize-job',
            entry: './resources/lambda/submit-summarize-glue-job.ts',
            role: glueJobLambdaRole,
            environment: {
                'GLUE_JOB_NAME': DeployConstant.GLUE_SUMMARIZE_JOB_NAME,
            },
            timeout: Duration.minutes(10),
            ...functionSettings
        });

        this.getSummaryResultsFunction = new lambdanodejs.NodejsFunction(this, 'GetSummaryResultsFunc', {
            functionName: 'get-summary-results-func',
            entry: './resources/lambda/summary-job-results.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                'TABLE_NAME': DeployConstant.GLUE_SUMMARY_TABLE,
                'DATABASE_NAME': DeployConstant.GLUE_DATABASE,
            },
            ...functionSettings
        });

        this.getSummaryJobsFunction = new lambdanodejs.NodejsFunction(this, 'GetSummaryJobsFunction', {
            functionName: 'get-summary-jobs-func',
            entry: './resources/lambda/get-summary-job-list.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'GLUE_SUMMARIZE_JOB_NAME': DeployConstant.GLUE_SUMMARIZE_JOB_NAME,
            },
            ...functionSettings
        });

         // 获取discord 1click job 列表
        this.getDiscord1ClickJobFunction = new lambdanodejs.NodejsFunction(this, 'GetDiscord1ClickJobFunction', {
            functionName: 'get-discord1click-job',
            entry: './resources/lambda/get-discord-1click-job.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'GLUE_DISCORD_1CLICK_JOB_NAME': DeployConstant.GLUE_DISCORD_1CLICK_JOB_NAME,
            },
            ...functionSettings
        });

        // 启动discord 1click job
        this.startDiscord1ClickJobFunction = new lambdanodejs.NodejsFunction(this, 'StartDiscord1ClickJobFunction', {
            functionName: 'start-discord1click-job',
            entry: './resources/lambda/start-discord-1click-job.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'GLUE_DISCORD_1CLICK_JOB_NAME': DeployConstant.GLUE_DISCORD_1CLICK_JOB_NAME,
            },
            ...functionSettings
        });

        // 修改Secret Lambda
        this.modifyDiscordSettingsFunction = new lambdanodejs.NodejsFunction(this, 'ModifyDiscordSettingsFunction', {
            functionName: 'modify-discord-settings',
            entry: './resources/lambda/modify-discord-settings.ts',
            role: glueJobLambdaRole,
            timeout: Duration.minutes(10),
            environment: {
                'BUCKET_NAME': DeployConstant.S3_BUCKET_NAME,
                'START_DISCORD_JOB_FUNC': this.startDiscord1ClickJobFunction.functionArn,
            },
            ...functionSettings
        });
    }

}
