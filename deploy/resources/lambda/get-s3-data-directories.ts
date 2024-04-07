const { S3Client, ListObjectsV2Command } = require('@aws-sdk/client-s3');

// Configure AWS SDK
const s3Client = new S3Client();

exports.handler = async (event, context) => {
    // Get the S3 bucket name and path prefix from environment variables
    const bucketName = process.env.BUCKET_NAME;
    const folderPrefix = process.env.RAW_DATA_PREFIX;

    try {
        // Call the ListObjectsV2 API to get all objects under the specified path
        const response = await s3Client.send(new ListObjectsV2Command({
            Bucket: bucketName,
            Prefix: folderPrefix,
            Delimiter: '/'
        }));

        // Parse the CommonPrefixes from the response, which contains all directory information
        const directories = response.CommonPrefixes?.map(item => item.Prefix);

        return {
            statusCode: 200,
            body: JSON.stringify(directories??[])
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Internal Server Error' })
        };
    }
};
