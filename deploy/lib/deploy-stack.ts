import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {CfnOutput} from "aws-cdk-lib";
import {GlueStack} from "./glue-stack";
import {LambdaStack} from "./lambda-stack";

export class DeployStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'DeployQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    const gluestack = new GlueStack(this,'glue-stack',{});
    const lambdastack = new LambdaStack(this,'lambda-stack',{});
    new CfnOutput(this, `Glue Job name`,{value:`${gluestack.jobName}`});


  }
}
