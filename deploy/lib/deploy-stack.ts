import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {CfnOutput} from "aws-cdk-lib";
import {GlueStack} from "./glue-stack";
import {LambdaStack} from "./lambda-stack";
import {ApigatewayStack} from "./apigateway-stack";
import {DynamodbStack} from "./dynamodb-stack";
import {S3Text} from "./s3";

export class DeployStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    const texts3 = new S3Text(this, "text_s3");
    const gluestack = new GlueStack(this,'glue-stack',{});
    const lambdastack = new LambdaStack(this,'lambda-stack',{});
    const apiGatewayStack = new ApigatewayStack(this, 'apigateway-stack', {
      promptTemplateFunction: lambdastack.promptTemplateFunction,
      startLLMAnalysisJobLambda: lambdastack.submitJobFunction,
      getGlueJobFunction: lambdastack.getGlueJobFunction,
      getAthenaResultsFunction: lambdastack.getAthenaResultsFunction,
      getRawDataDirectoriesFunction: lambdastack.getRawDataDirectoriesFunction,
    })
    apiGatewayStack.addDependency(lambdastack);
    const dynamodbStack = new DynamodbStack(this,'dynamodb-stack',{});
    new CfnOutput(this, `Glue Job name`,{value:`${gluestack.jobName}`});


  }
}
