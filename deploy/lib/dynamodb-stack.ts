import {NestedStack, RemovalPolicy} from "aws-cdk-lib";
import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {DeployConstant} from "./deploy-constants";
import { AttributeType, Table, } from "aws-cdk-lib/aws-dynamodb";

export class DynamodbStack extends NestedStack {

    /**
     *
     * @param {Construct} scope
     * @param {string} id
     * @param {StackProps=} props
     */
    constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
        super(scope, id, props);

        const prompt_template_table = new Table(this, "prompt_template", {
            tableName: DeployConstant.LLM_ANALYSIS_TEXT_TABLE_NAME,
            partitionKey: {
                name: "id",
                type: AttributeType.STRING,
            },
            pointInTimeRecovery: true,
            removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
        });

        const readScaling = prompt_template_table.autoScaleReadCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        readScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const writeScaling = prompt_template_table.autoScaleWriteCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        writeScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const webhook_settings_table = new Table(this, "webhook_settings_table", {
            tableName: DeployConstant.DDB_WEBHOOK_SETTINGS_TABLE,
            partitionKey: {
                name: "id",
                type: AttributeType.STRING,
            },
            pointInTimeRecovery: true,
            removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
        });

        const webhookReadScaling = webhook_settings_table.autoScaleReadCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        webhookReadScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const webhookWriteScaling = webhook_settings_table.autoScaleWriteCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        webhookWriteScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const category_settings_table = new Table(this, "category_settings_table", {
            tableName: DeployConstant.DDB_CATEGORY_SETTINGS_TABLE,
            partitionKey: {
                name: "id",
                type: AttributeType.STRING,
            },
            pointInTimeRecovery: true,
            removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
        });

        const categoryReadScaling = category_settings_table.autoScaleReadCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        categoryReadScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const categoryWriteScaling = category_settings_table.autoScaleWriteCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        categoryWriteScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const user_jobs_table = new Table(this, "user_jobs_table", {
            tableName: DeployConstant.DDB_USER_JOBS_TABLE,
            partitionKey: {
                name: "id",
                type: AttributeType.STRING,
            },
            pointInTimeRecovery: true,
            removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
        });

        const userJobsReadScaling = user_jobs_table.autoScaleReadCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        userJobsReadScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

        const userJobsWriteScaling = user_jobs_table.autoScaleWriteCapacity({
            minCapacity: 1,
            maxCapacity: 10,
        });

        userJobsWriteScaling.scaleOnUtilization({
            targetUtilizationPercent: 65,
        });

    }
}
