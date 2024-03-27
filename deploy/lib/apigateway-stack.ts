import {
    NestedStack,
    aws_apigateway as _apigateway,
    Duration, NestedStackProps
} from "aws-cdk-lib";
import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";

export interface APIGatewayProps extends NestedStackProps {
    startLLMAnalysisJobLambda: lambda.IFunction,
}

export class ApigatewayStack extends NestedStack {

    constructor(scope: Construct, id: string, props: APIGatewayProps) {
        super(scope, id, props);

        const stageName = 'prod';
        const llmTextAnalysisAPI = new _apigateway.RestApi(this, 'LLM-TEXT-ANALYSIS-API', {
            restApiName: 'LLM-TEXT-ANALYSIS-API',
            retainDeployments: false,
            deploy: true,
            deployOptions: {
                stageName: stageName,
                cacheClusterEnabled: true,
                cacheClusterSize: '0.5',
                cacheTtl: Duration.minutes(1),
                throttlingBurstLimit: 100,
                throttlingRateLimit: 1000
            },
            endpointTypes: [
                _apigateway.EndpointType.EDGE
            ],
        });

        const apiKey = new _apigateway.ApiKey(this, 'LLM-TEXT-ANALYSIS-API-KEY', {
            apiKeyName: 'LLM-TEXT-ANALYSIS-API-KEY',
            enabled: true,
            description: 'LLM-TEXT-ANALYSIS-API-KEY'
        });
        const startAnalysisRootPath = llmTextAnalysisAPI.root.addResource('start-analysis-job', {
            defaultMethodOptions: {
                apiKeyRequired: true
            }
        });

        startAnalysisRootPath.addMethod('POST', new _apigateway.LambdaIntegration(props.startLLMAnalysisJobLambda));

        const usagePlan = llmTextAnalysisAPI.addUsagePlan('TestAPIKeyUsagePlan', {
            name: 'Test-GLWorkshop-UsagePlan',
            throttle: {
                burstLimit: 10,
                rateLimit: 100
            },
            quota: {
                limit: 1000,
                offset: 0,
                period: _apigateway.Period.DAY
            },
            apiStages: [
                {
                    api: llmTextAnalysisAPI,
                    stage: llmTextAnalysisAPI.deploymentStage,
                }
            ]
        });
        usagePlan.addApiKey(apiKey)
        new cdk.CfnOutput(scope, 'API-Key ARN', { value: apiKey.keyArn })
        new cdk.CfnOutput(scope, 'InvokeUrl', { value: llmTextAnalysisAPI.url })
    }
}
