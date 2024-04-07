import { GlueClient, StartJobRunCommand } from "@aws-sdk/client-glue";

const client = new GlueClient();
const jobName = process.env.GLUE_JOB_NAME;
const bucketName = process.env.BUCKET_NAME;
const rawDataPrefix = process.env.RAW_DATA_PREFIX;
const promptTemplateTable = process.env.PROMPT_TEMPLATE_TABLE;

exports.handler = async (event,context) => {
    let body;
    try {
        body = JSON.parse(event.body);
    } catch (err) {
        return {
            statusCode: 400,
            body: JSON.stringify('参数错误'),
        };
    }

    if (!body.prompt_id || !body.prefix) {
        return {
            statusCode: 400,
            body: JSON.stringify('缺少必要参数'),
        };
    }

    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
        Arguments: {
            '--PROMPT_ID': body.prompt_id,
            '--BUCKET_NAME': bucketName,
            '--PROMPT_TEMPLATE_TABLE': promptTemplateTable,
            '--RAW_DATA_PREFIX': body.prefix,
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
