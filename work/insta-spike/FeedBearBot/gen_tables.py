import boto3
import time

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')


table = dynamodb.create_table(
    TableName='dev.smm.ig.profiles',
    KeySchema=[
        {
            'AttributeName': 'ScanUntil',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'ProfileName',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'ProfileName',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'ScanUntil',
            'AttributeType': 'N'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
)

print("Table status:", table.table_status)
time.sleep(10)
dynamodbc = boto3.client('dynamodb', region_name='us-west-2')
response = dynamodbc.describe_table(TableName='dev.smm.ig.profiles')
print("Table status:", response['Table']['TableStatus'])

table = dynamodb.create_table(
    TableName='dev.smm.ig.stories',
    KeySchema=[
        {
            'AttributeName': 'ProfileName',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'StoryId',
            'KeyType': 'RANGE' #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'ProfileName',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'StoryId',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
)

print("Table status:", table.table_status)
time.sleep(10)
response = dynamodbc.describe_table(TableName='dev.smm.ig.stories')
print("Table status:", response['Table']['TableStatus'])

