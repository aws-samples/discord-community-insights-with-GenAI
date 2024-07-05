const { DynamoDBClient, GetItemCommand, PutItemCommand, UpdateItemCommand, DeleteItemCommand, ScanCommand, QueryCommand } = require('@aws-sdk/client-dynamodb');
const { marshall, unmarshall } = require('@aws-sdk/util-dynamodb');
const crypto = require('crypto');
const tableName = process.env.TABLE_NAME;
const pageSize = 20;

const ddbClient = new DynamoDBClient();

exports.handler = async (event) => {
    console.log(event);

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
    if (event.pathParameters && event.pathParameters.id) {
        console.log(event.pathParameters.id);
        const params = {
            TableName: tableName,
            Key: marshall({ id: event.pathParameters.id }),
        };

        const { Item } = await ddbClient.send(new GetItemCommand(params));

        if (!Item) {
            return buildResponse(404, '{"message": "Item not found"}');
        }

        return buildResponse(200, JSON.stringify(unmarshall(Item)));
    } else {
        const params = {
            TableName: tableName,
            Limit: 20,
        };

        const { Items } = await ddbClient.send(new ScanCommand(params));
        return buildResponse(200, JSON.stringify(Items.map(unmarshall)));
    }
}

async function queryWithPagination(lastEvaluatedKey, queryParams) {
    const params = {
        TableName: tableName,
        Limit: pageSize,
        ExclusiveStartKey: lastEvaluatedKey,
        // 其他查询条件...
    };

    // 合并额外的查询参数
    Object.assign(params, queryParams);

    const result = await ddbClient.send(new QueryCommand(params));
    const items = result.Items.map(unmarshall);
    const lastKey = result.LastEvaluatedKey;

    if (lastKey) {
        // 有更多数据需要获取
        const nextItems = await queryWithPagination(lastKey, queryParams);
        items.push(...nextItems);
    }

    return items;
}

async function putDynamoDBData(event) {
    let item = JSON.parse(event.body);
    console.log(item);
    if (!item.id) {
        item['id'] = crypto.randomUUID();
        item['created_at'] = Date.now();
    }
    const params = {
        TableName: tableName,
        Item: marshall(item),
    };

    await ddbClient.send(new PutItemCommand(params));
    return buildResponse(200, '{"message": "Item added"}');
}

async function updateDynamoDBData(event) {
    let body = JSON.parse(event.body);
    const params = {
        TableName: tableName,
        Key: marshall({ id: event.pathParameters.id }),
        UpdateExpression: 'set #t = :topic, #pr = :prompt_rag, #ps = :prompt_sentiment, #c= :created_at',
        ExpressionAttributeNames: {
            '#t': 'topic',
            '#pr': 'prompt_rag',
            '#ps': 'prompt_sentiment',
            '#c': 'created_at',
        },
        ExpressionAttributeValues: marshall({
            ':topic': body.topic,
            ':prompt_rag': body.prompt_rag,
            ':prompt_sentiment': body.prompt_sentiment,
            ':created_at': Date.now(),
        }),
        ReturnValues: 'ALL_NEW',
    };

    console.log(params);

    const { Attributes } = await ddbClient.send(new UpdateItemCommand(params));

    if (!Attributes) {
        return buildResponse(404, '{"message": "Item not found"}');
    }

    return buildResponse(200, JSON.stringify(unmarshall(Attributes)));
}

async function deleteDynamoDBData(event) {
    const params = {
        TableName: tableName,
        Key: marshall({ id: event.pathParameters.id }),
    };

    await ddbClient.send(new DeleteItemCommand(params));
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
