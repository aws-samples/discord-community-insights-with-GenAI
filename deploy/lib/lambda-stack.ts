import * as cdk from 'aws-cdk-lib';
import {NestedStack} from 'aws-cdk-lib';
import * as lambdanodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";
import * as dotenv from "dotenv";

dotenv.config();

export class LambdaStack extends NestedStack {

    constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
        super(scope, id, props);

        const lambdaRole = new iam.Role(this, 'ApigLambdaRole', {
            roleName: `lambda--${cdk.Stack.of(this).region}`,
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchFullAccess'),
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

        const functionSettings : lambdanodejs.NodejsFunctionProps = {
            handler: 'handler',
            runtime: lambda.Runtime.NODEJS_LATEST,
            memorySize: 128,
            timeout: cdk.Duration.seconds(60),
            architecture: cdk.aws_lambda.Architecture.X86_64,
            role: lambdaRole,
            logRetention: cdk.aws_logs.RetentionDays.ONE_WEEK
        }

        const codeToTokensFunction = new lambdanodejs.NodejsFunction(this, 'SubmitGlueJob', {
            functionName: 'submit-glue-job-func',
            entry: './resources/lambda/submit-analysis-glue-job.ts',
            environment: {
                'GLUE_JOB_NAME': DeployConstant.GLUE_JOB_NAME,
            },
            ...functionSettings
        });
    }

}
