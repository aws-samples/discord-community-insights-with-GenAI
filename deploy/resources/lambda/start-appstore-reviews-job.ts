import { GlueClient, StartJobRunCommand, StartJobRunCommandOutput } from "@aws-sdk/client-glue";

const glueClient = new GlueClient({});

exports.handler = async (event: { secretName: string }) => {
    const jobName = process.env.GLUE_APPSTORE_JOB_NAME;
    const results = await startGlueJob(glueClient, jobName, event.user_job_id);

    console.log("Glue作业启动成功", results);
    return {
        statusCode: 200,
        body: JSON.stringify('Glue作业启动成功'),
    };
};

async function startGlueJob(client: GlueClient, jobName: string, user_job_id: string): Promise<StartJobRunCommandOutput> {
    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
        Arguments: {
            '--USER_JOB_ID': user_job_id,
        },
    });
    const data = await client.send(startJobRunCommand);
    return data;
}