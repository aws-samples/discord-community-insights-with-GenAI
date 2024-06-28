import { GlueClient, StartJobRunCommand, StartJobRunCommandOutput } from "@aws-sdk/client-glue";
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const glueClient = new GlueClient({});
const secretsManagerClient = new SecretsManagerClient({});

exports.handler = async (event: { secretName: string }) => {
    const secretValue = await getSecretValue(event.secretName);
    const channelIds = secretValue.CHANNEL_ID.split('\n');

    const jobName = process.env.GLUE_DISCORD_1CLICK_JOB_NAME;
    const results = await Promise.all(channelIds.map(channelId => startGlueJob(glueClient, jobName, channelId, event.secretName)));

    console.log("Glue作业启动成功", results);
    return {
        statusCode: 200,
        body: JSON.stringify('Glue作业启动成功'),
    };
};

async function getSecretValue(secretName: string): Promise<{ CHANNEL_ID: string }> {
    const input = { SecretId: secretName };
    const command = new GetSecretValueCommand(input);
    const response = await secretsManagerClient.send(command);
    const secretValue = JSON.parse(response.SecretString);
    return secretValue;
}

async function startGlueJob(client: GlueClient, jobName: string, channelId: string, secretName: string): Promise<StartJobRunCommandOutput> {
    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
        Arguments: {
            '--CHANNEL_ID': channelId,
            '--SECRET_NAME': secretName,
        },
    });
    const data = await client.send(startJobRunCommand);
    return data;
}