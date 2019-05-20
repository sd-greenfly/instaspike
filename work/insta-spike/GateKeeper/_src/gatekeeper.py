import boto3
from datetime import datetime
import json
import time


profile_table_name = "dev.smm.ig.profiles"
story_table_name = "dev.smm.ig.stories"

def store_username_db(igprofile):
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.put_item(
        TableName=profile_table_name,
        Item={
            'ScanUntil': {'N': str(int(time.time())+172800)},
            'ProfileName': {'S': igprofile}
        }
    )
    response = dynamodb_client.scan(
        TableName=profile_table_name,
        Select='ALL_ATTRIBUTES',
        FilterExpression="#name0 = :value0",
        ExpressionAttributeNames={
            "#name0": "ProfileName"
        },
        ExpressionAttributeValues={
            ":value0": {
                'S': igprofile
            }
        }
    )
    key_list = []
    for item in response["Items"]:
        key_list.append(item["ScanUntil"]["N"])
    key_list.sort()
    key_list.pop()
    for key in key_list:
        dynamodb_client.delete_item(
            TableName='dev.smm.ig.profiles',
            Key={
                'ScanUntil': {
                    'N': str(key)
                },
                'ProfileName': {
                    'S': igprofile
                }
            }
        )


def retrieve_available_stories(igprofile):
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.scan(
        TableName=story_table_name,
        Select='ALL_ATTRIBUTES',
        FilterExpression="#name0 = :value0",
        ExpressionAttributeNames={
            "#name0": "ProfileName"
        },
        ExpressionAttributeValues={
            ":value0": {
                'S': igprofile
            }
        }
    )
    story_list = []
    for item in response["Items"]:
        print(datetime.fromtimestamp(int(item["FoundTime"]["N"])))
        item_dict = {
            "url": item["StoryLocation"]['S'],
            "type": item["Type"]['S'],
            "date_found": datetime.fromtimestamp(int(item["FoundTime"]["N"])).strftime('%Y-%m-%d %H:%M:%S')
        }
        story_list.append(item_dict)
    return story_list


def handler(event,context):
    if event["queryStringParameters"] is None or "igprofile" not in event["queryStringParameters"]:
        body = "We need you to pass in an Instagram username as igprofile."
    else:
        igprofile = event["queryStringParameters"]["igprofile"]
        store_username_db(igprofile)
        stories = retrieve_available_stories(igprofile)
        body = json.dumps(stories)
    response = {
        "statusCode": 200,
        "headers": {
            "x-custom-header": "testing"
        },
        "body": body
    }
    return response
