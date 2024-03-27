const AWS = require('aws-sdk');
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
    let response;

    switch (event.httpMethod) {
        case 'GET':
            response = await getDynamoDBData(event);
            break;
        case 'POST':
            response = await putDynamoDBData(event);
            break;
        case 'PUT':
            response = await updateDynamoDBData(event);
            break;
        case 'DELETE':
            response = await deleteDynamoDBData(event);
            break;
        default:
            response = buildResponse(404, '{"message": "Unsupported method"}');
    }

    return response;
};

async function getDynamoDBData(event) {
    const params = {
        TableName: tableName,
        Key: {
            id: event.pathParameters.id,
        },
    };

    const data = await dynamoDb.get(params).promise();

    if (!data.Item) {
        return buildResponse(404, '{"message": "Item not found"}');
    }

    return buildResponse(200, JSON.stringify(data.Item));
}

async function putDynamoDBData(event) {
    const params = {
        TableName: tableName,
        Item: JSON.parse(event.body),
    };

    await dynamoDb.put(params).promise();

    return buildResponse(200, '{"message": "Item added"}');
}

async function updateDynamoDBData(event) {
    const params = {
        TableName: tableName,
        Key: {
            id: event.pathParameters.id,
        },
        UpdateExpression: 'set #d = :data',
        ExpressionAttributeNames: {
            '#d': 'data',
        },
        ExpressionAttributeValues: {
            ':data': JSON.parse(event.body).data,
        },
        ReturnValues: 'ALL_NEW',
    };

    const data = await dynamoDb.update(params).promise();

    if (!data.Attributes) {
        return buildResponse(404, '{"message": "Item not found"}');
    }

    return buildResponse(200, JSON.stringify(data.Attributes));
}

async function deleteDynamoDBData(event) {
    const params = {
        TableName: tableName,
        Key: {
            id: event.pathParameters.id,
        },
    };

    const data = await dynamoDb.delete(params).promise();

    if (!data.Attributes) {
        return buildResponse(404, '{"message": "Item not found"}');
    }

    return buildResponse(200, '{"message": "Item deleted"}');
}

function buildResponse(statusCode, body) {
    return {
        statusCode,
        headers: {
            'Content-Type': 'application/json',
        },
        body,
    };
}
