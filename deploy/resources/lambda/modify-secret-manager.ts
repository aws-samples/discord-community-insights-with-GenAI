import { SecretsManagerClient, PutSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import { EventBridgeClient, PutRuleCommand } from "@aws-sdk/client-eventbridge";

const client = new SecretsManagerClient({});
const ebclient = new EventBridgeClient({});
const secret_arn = process.env.SECRET_ARN;
const rule_name = process.env.RULE_NAME;


exports.handler = async (event,context) => {

    console.log(event);
    let body = JSON.parse(event.body);
    const newSecretValue = JSON.stringify({
        CHANNEL_ID: body.channel_id,
        TOKEN: body.token,
        RUNNING_CYCLE: body.running_cycle,
        DATA_PERIOD: body.data_period,
    })
    console.log(newSecretValue)
    const command = new PutSecretValueCommand({
        SecretId: secret_arn,
        SecretString: newSecretValue,
    });

    try {
        const response = await client.send(command);
        console.log(`密钥已成功更新为: ${newSecretValue}`);

        const input = { // PutRuleRequest
            Name: rule_name, // required
            ScheduleExpression: body.running_cycle,
            State: "ENABLED",
        };
        const putRuleCommand = new PutRuleCommand(input);
        const ebresponse = await ebclient.send(putRuleCommand);
        console.log(ebresponse)

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(response)
        };

    } catch (err) {
        console.error(err);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(err)
        };

    }
};