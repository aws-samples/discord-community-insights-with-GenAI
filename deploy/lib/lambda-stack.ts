import * as cdk from 'aws-cdk-lib';
import {Duration, NestedStack} from 'aws-cdk-lib';
import * as lambdanodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";
import {DeployConstant} from "./deploy-constants";

export class LambdaStack extends NestedStack {

    public readonly submitJobFunction: lambda.IFunction;
    public readonly promptTemplateFunction: lambda.IFunction;
    public readonly getGlueJobFunction: lambda.IFunction;
    public readonly getAthenaResultsFunction: lambda.IFunction;
    public readonly getRawDataDirectoriesFunction: lambda.IFunction;
    public readonly submitSummarizeJobFunction: lambda.IFunction;
    public readonly getSummaryResultsFunction: lambda.IFunction;
    public readonly getSummaryJobsFunction: lambda.IFunction;

    constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
        super(scope, id, props);

        const glueJobLambdaRole = new iam.Role(this, 'ApigLambdaRole', {
            roleName: `submit-job-lambda--${cdk.Stack.of(this).region}`,
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAthenaFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
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
    }

}
