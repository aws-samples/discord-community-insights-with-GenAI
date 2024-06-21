const { GlueClient, GetJobRunsCommand } = require("@aws-sdk/client-glue");

const jobName = process.env.GLUE_DISCORD_1CLICK_JOB_NAME;
const pageSize = 10;

exports.handler = async (event,context) => {
    const glueClient = new GlueClient();

    const params = {
        JobName: jobName,
        MaxResults: pageSize,
    };

    if (event.queryStringParameters && event.queryStringParameters.page_token) {
        params.NextToken = event.queryStringParameters.page_token;
    }

    const command = new GetJobRunsCommand(params);

    try {
        const response = await glueClient.send(command);
        const jobRuns = response.JobRuns;
        const nextPageToken = response.NextToken;

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jobRuns,
                nextPageToken
            })
        };
    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};