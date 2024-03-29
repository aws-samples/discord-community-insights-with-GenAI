const AWS = require('aws-sdk');
const glue = new AWS.Glue();

const jobName = process.env.GLUE_JOB_NAME;
const pageSize = 10;
exports.handler = async (event) => {
    const pageToken = event.queryStringParameters.pageToken;

    const params = {
        Name: jobName,
        MaxResults: pageSize,
        NextToken: pageToken
    };

    const response = await glue.getJobRuns(params).promise();
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
};
