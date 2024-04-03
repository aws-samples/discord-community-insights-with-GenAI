import { GlueClient, StartJobRunCommand } from "@aws-sdk/client-glue";

const client = new GlueClient();
const jobName = process.env.GLUE_JOB_NAME;
const bucketName = process.env.BUCKET_NAME;
const rawDataPrefix = process.env.RAW_DATA_PREFIX;
const promptTemplateTable = process.env.PROMPT_TEMPLATE_TABLE;
exports.handler = async (event) => {

    let body = JSON.parse(event.body);

    if (!body.prompt_id || !body.prefix) {
        return {
            statusCode: 400,
            body: JSON.stringify('参数错误'),
        };
    }


    // 创建启动Glue作业的命令
    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
        // 如果需要，可以在这里添加其他参数，例如Arguments用于传递给Glue作业的参数
        Arguments: {
            '--PROMPT_ID': body.prompt_id,
            '--BUCKET_NAME': bucketName,
            '--PROMPT_TEMPLATE_TABLE': promptTemplateTable,
            '--RAW_DATA_PREFIX': body.prefix
        }
    });

    try {
        // 发送命令以启动Glue作业
        const data = await client.send(startJobRunCommand);
        console.log("Glue作业启动成功", data);
        // 返回成功响应
        return {
            statusCode: 200,
            body: JSON.stringify('Glue作业启动成功'),
        };
    } catch (err) {
        console.error("启动Glue作业失败", err);
        // 返回错误响应
        return {
            statusCode: 500,
            body: JSON.stringify('启动Glue作业失败'),
        };
    }
};
