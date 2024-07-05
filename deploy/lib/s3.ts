import {Construct} from "constructs";
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cdk from 'aws-cdk-lib';
import {DeployConstant} from "./deploy-constants";

export class S3Text extends Construct {

    public readonly textS3: s3.Bucket

    constructor(scope: Construct, id: string) {
        super(scope, id);
        // Create S3
        this.textS3 = new s3.Bucket(this, 'MyBucket', {
            bucketName: DeployConstant.S3_BUCKET_NAME,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            publicReadAccess: false,
            autoDeleteObjects: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY, // destroy s3 when delete stack.
        });

        // Output S3
        new cdk.CfnOutput(this, 'S3 bucket', {
            value: this.textS3.bucketName
        });
    }
}
