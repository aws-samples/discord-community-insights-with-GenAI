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
    promptTemplateFunction: lambda.IFunction,
    getGlueJobFunction: lambda.IFunction,
    getAthenaResultsFunction: lambda.IFunction,
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
        const jobsRootPath = llmTextAnalysisAPI.root.addResource('jobs', {
            defaultMethodOptions: {
                apiKeyRequired: true
            }
        });

        const promptsRootPath = llmTextAnalysisAPI.root.addResource('prompts', {
            defaultMethodOptions: {
                apiKeyRequired: true
            }
        });

        jobsRootPath.addMethod('POST', new _apigateway.LambdaIntegration(props.startLLMAnalysisJobLambda));
        jobsRootPath.addMethod('GET', new _apigateway.LambdaIntegration(props.getGlueJobFunction), {
            requestParameters: {
                'method.request.querystring.page_token': false
            }
        });

        const resultsPath = jobsRootPath.addResource("results", {
            defaultMethodOptions: {
                apiKeyRequired: true
            }
        });
        const resultsGetMethod = resultsPath.addMethod("POST",
            new _apigateway.LambdaIntegration(props.getAthenaResultsFunction), {
                requestParameters: {
                    'method.request.querystring.body': true
                }
            })

        promptsRootPath.addMethod("GET", new _apigateway.LambdaIntegration(props.promptTemplateFunction))
        promptsRootPath.addMethod("POST", new _apigateway.LambdaIntegration(props.promptTemplateFunction))

        const singlePromptPath = promptsRootPath.addResource('{id}', {
            defaultMethodOptions: {
                apiKeyRequired: true
            }
        });

        singlePromptPath.addMethod("GET", new _apigateway.LambdaIntegration(props.promptTemplateFunction))
        singlePromptPath.addMethod("PUT", new _apigateway.LambdaIntegration(props.promptTemplateFunction))
        singlePromptPath.addMethod("DELETE", new _apigateway.LambdaIntegration(props.promptTemplateFunction))

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
