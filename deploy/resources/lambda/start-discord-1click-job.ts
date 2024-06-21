import { GlueClient, StartJobRunCommand } from "@aws-sdk/client-glue";

const client = new GlueClient();
const jobName = process.env.GLUE_DISCORD_1CLICK_JOB_NAME;

exports.handler = async (event,context) => {

    console.log(event)
    const startJobRunCommand = new StartJobRunCommand({
        JobName: jobName,
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
