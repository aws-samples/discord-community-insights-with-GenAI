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
            removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
        });
    }
}
