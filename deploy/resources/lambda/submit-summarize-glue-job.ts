import { GlueClient, StartJobRunCommand } from "@aws-sdk/client-glue";

const client = new GlueClient();
const jobName = process.env.GLUE_JOB_NAME;

exports.handler = async (event,context) => {

    console.log(event)
    let body;
    try {
        body = JSON.parse(event.body);
    } catch (err) {
        return {
            statusCode: 400,
            body: JSON.stringify('参数错误'),
        };
    }

    if (!body.analysis_job_id) {
        return {
            statusCode: 400,
            body: JSON.stringify('缺少必要参数analysis_job_id'),
        };
    }

    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
        Arguments: {
            '--ANALYSIS_JOB_ID': body.analysis_job_id,
        },
    });

    try {
        const data = await client.send(startJobRunCommand);
        console.log("Glue作业启动成功", data);
        return {
            statusCode: 200,
            body: JSON.stringify('Glue作业启动成功'),
        };
    } catch (err) {
        console.error("启动Glue作业失败", err);
        return {
            statusCode: 500,
            body: JSON.stringify('启动Glue作业失败'),
        };
    }
};
