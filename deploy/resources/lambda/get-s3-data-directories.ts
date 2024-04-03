const AWS = require('aws-sdk');

// 配置 AWS SDK
const s3 = new AWS.S3();
exports.handler = async (event, context) => {
    // 从环境变量中获取 S3 桶名称和路径前缀
    const bucketName = process.env.BUCKET_NAME;
    const folderPrefix = process.env.RAW_DATA_PREFIX;

    try {
        // 调用 ListObjectsV2 API 获取指定路径下的所有对象
        const response = await s3.listObjectsV2({
            Bucket: bucketName,
            Prefix: folderPrefix,
            Delimiter: '/'
        }).promise();

        // 解析响应中的 CommonPrefixes，这个字段包含所有目录信息
        const directories = response.CommonPrefixes.map(item => item.Prefix);

        return {
            statusCode: 200,
            body: JSON.stringify(directories)
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Internal Server Error' })
        };
    }
};
