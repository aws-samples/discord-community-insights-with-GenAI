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
    }
}
