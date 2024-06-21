import { SecretsManagerClient, PutSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({});
const secret_arn = process.env.SECRET_ARN;

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