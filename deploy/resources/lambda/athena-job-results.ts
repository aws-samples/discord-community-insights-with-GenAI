const AWS = require('aws-sdk');

const tableName = process.env.TABLE_NAME;
const dbName = process.env.DATABASE_NAME;
const bucketName = process.env.BUCKET_NAME;
const athena = new AWS.Athena();

exports.handler = async (event, context) => {
    let queryBody = JSON.parse(event.body);
    if (!queryBody || !queryBody.job_id) {
        return {
            statusCode: 400,
            body: JSON.stringify({'error': 'parameter job_id needed~!'})
        };
    }
    const job_id = queryBody.job_id;

    let queryString = `SELECT * FROM ${tableName} WHERE job_id='${job_id}'`;
    if (queryBody.sql) {
        queryString = queryBody.sql
    }
    console.log("query string:", queryString);
    // 设置 Athena 查询参数
    const params = {
        QueryString: queryString,
        QueryExecutionContext: {
            Database: dbName
        },
        ResultConfiguration: {
            OutputLocation: 's3://' + bucketName + '/athena-query-results/'
        }
    };
    console.log(params)
    try {
        // 执行 Athena 查询
        const data = await athena.startQueryExecution(params).promise();

        // 获取查询结果的执行 ID
        const queryExecutionId = data.QueryExecutionId;

        // 轮询查询状态
        let queryStatus = 'QUEUED';
        while (queryStatus === 'QUEUED' || queryStatus === 'RUNNING') {
            const result = await athena.getQueryExecution({ QueryExecutionId: queryExecutionId }).promise();
            queryStatus = result.QueryExecution.Status.State;
            console.log('Query Status:', queryStatus);
            if (queryStatus === 'QUEUED' || queryStatus === 'RUNNING') {
                // 查询仍在进行中，等待一段时间再次轮询
                await new Promise(resolve => setTimeout(resolve, 5000)); // 等待5秒
            }
        }

        // 获取查询结果
        const result = await athena.getQueryResults({ QueryExecutionId: queryExecutionId }).promise();

        // 输出查询结果
        console.log('Query Results:', result);

        return {
            statusCode: 200,
            body: JSON.stringify(result)
        };
    } catch (err) {
        console.error('Error executing Athena query:', err);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Error executing Athena query' })
        };
    }
};
