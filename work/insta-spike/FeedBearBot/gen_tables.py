import boto3
import json
import os
import time


# configurations from file
config_filename = "_src/configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"
region_name = all_configs['region'] if 'region' in all_configs.keys() else "us-west-2"

profile_table_name = "{}.smm.ig.profiles".format(environment)
story_table_name = "{}.smm.ig.stories".format(environment)
credential_table_name = "{}.smm.ig.credentials".format(environment)

dynamodb = boto3.resource('dynamodb', region_name=region_name)

table = dynamodb.create_table(
    TableName=profile_table_name,
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
dynamodbc = boto3.client('dynamodb', region_name=region_name)
response = dynamodbc.describe_table(TableName=profile_table_name)
print("Table status:", response['Table']['TableStatus'])

table = dynamodb.create_table(
    TableName=story_table_name,
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
response = dynamodbc.describe_table(TableName=story_table_name)
print("Table status:", response['Table']['TableStatus'])

table = dynamodb.create_table(
    TableName=credential_table_name,
    KeySchema=[
        {
            'AttributeName': 'ProfileName',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'ProfileId',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'ProfileName',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'ProfileId',
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
response = dynamodbc.describe_table(TableName=credential_table_name)
print("Table status:", response['Table']['TableStatus'])
