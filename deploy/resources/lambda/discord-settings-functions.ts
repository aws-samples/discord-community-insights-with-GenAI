import { SecretsManagerClient, PutSecretValueCommand, DescribeSecretCommand, CreateSecretCommand, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import { EventBridgeClient, PutRuleCommand, PutTargetsCommand } from "@aws-sdk/client-eventbridge";

const client = new SecretsManagerClient({});
const ebclient = new EventBridgeClient({});
let secret_arn = '';
const START_DISCORD_JOB_FUNC = process.env.START_DISCORD_JOB_FUNC;
const SECRET_PREFIX = 'discord-setting-'
const RULE_PREFIX = 'discord-rule-'


exports.handler = async (event,context) => {

    console.log(event);

    let response;

    switch (event.httpMethod) {
        case 'GET':
            response = await getDiscordSettings(event);
            break;
        case 'POST':
            response = await modifyDiscordSettings(event);
            break;
        default:
            response = buildResponse(404, '{"message": "Unsupported method"}');
    }
    return response;
};

async function getDiscordSettings(event) {
    if (event.pathParameters && event.pathParameters.username) {
        const secretName = SECRET_PREFIX + event.pathParameters.username;
        console.log("-------------------" + secretName);
        const input = { SecretId: secretName };
        const command = new GetSecretValueCommand(input);
        const response = await client.send(command);
        const secretValue = response.SecretString;
        console.log("-------------------secretValue: " + secretValue);
        return buildResponse(200, secretValue)
    } else {
        return buildResponse(500, '{"message": "please provide username"}')
    }
}

async function modifyDiscordSettings(event) {
    let body = JSON.parse(event.body);
    let username = body.username;
    let secretName = SECRET_PREFIX + username

    //判断当前用户是否已经创建了Secret
    try {
        // 尝试描述机密
        const describeSecretCommand = new DescribeSecretCommand({ SecretId: secretName });
        const describeSecretResponse = await client.send(describeSecretCommand);
        console.log(describeSecretResponse);
        secret_arn = describeSecretResponse.ARN;
    } catch (err) {
        if (err.name === "ResourceNotFoundException") {
            console.log(`Secret ${secretName} does not exist`);
        } else {
            // 处理其他异常
            console.error("Error:", err);
        }
    }

    try {
        const newSecretValue = JSON.stringify({
            USER_NAME: username,
            CHANNEL_ID: body.channel_id,
            TOKEN: body.token,
            RUNNING_CYCLE: body.running_cycle,
            DATA_PERIOD: body.data_period,
        })
        console.log(newSecretValue)

        // 如果该用户还没有创建过Secret,则创建
        if (secret_arn && secret_arn !== '') {
            const command = new PutSecretValueCommand({
                SecretId: secret_arn,
                SecretString: newSecretValue,
            });
            const response = await client.send(command);
            console.log(`密钥已成功更新为: ${newSecretValue}`);
        } else {
            const params = {
                Name: secretName,
                SecretString: newSecretValue,
            };
            const command = new CreateSecretCommand(params);
            const response = await client.send(command);
            console.log(`Secret ${secretName} created successfully`);
            console.log("Response:", response);
        }

        // 为当前用户创建EventBridge Schedule
        const ruleName = RULE_PREFIX + username;
        const input = { // PutRuleRequest
            Name: ruleName, // required
            ScheduleExpression: body.running_cycle,
            State: "ENABLED",
            Description: 'Rule For User: ' + username,
        };
        const putRuleCommand = new PutRuleCommand(input);
        const ebresponse = await ebclient.send(putRuleCommand);
        console.log(ebresponse)

        //为EventBridge Rule绑定Lambda
        const putTargetsCommand = new PutTargetsCommand({
            Rule: ruleName,
            Targets: [{ Id: 'LambdaTarget' + username, Arn: START_DISCORD_JOB_FUNC, Input: JSON.stringify({secretName: secretName}) }]
        })
        const response = await ebclient.send(putTargetsCommand);
        console.log(response);
        console.log(`Target added to rule ${ruleName} successfully`);

        return buildResponse(200, JSON.stringify(ebresponse));

    } catch (err) {
        console.error(err);
        return buildResponse(500, JSON.stringify(err));
    }
}


function buildResponse(statusCode:Number, body) {
    return {
        statusCode,
        headers: {
            'Content-Type': 'application/json',
        },
        body,
    };
}