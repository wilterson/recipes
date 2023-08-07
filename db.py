import boto3

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')


def create_table(table_name):
    ''' Create a table '''
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'key',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)


def put_item(table_name, item):
    ''' Put an item in the table '''
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)


def get_item(table_name, id):
    ''' Get an item from the table '''
    table = dynamodb.Table(table_name)
    response = table.get_item(
        Key={
            'key': id
        }
    )

    return response['Item'] if 'Item' in response else None


def get_all_items(table_name):
    ''' Get all items in the table '''
    table = dynamodb.Table(table_name)
    response = table.scan()

    return response['Items'] if 'Items' in response else None
