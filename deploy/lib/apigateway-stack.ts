import {NestedStack} from "aws-cdk-lib";
import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";

export class ApigatewayStack extends NestedStack {

    constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
        super(scope, id, props);



    }
}
