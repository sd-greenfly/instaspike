import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import json
import os
import time

# configurations from file
config_filename = "configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"


profile_table_name = "{}.smm.ig.profiles".format(environment)
story_table_name = "{}.smm.ig.stories".format(environment)
dynamodb_resource = boto3.resource('dynamodb')


def store_username_db(igprofile):
    table = dynamodb_resource.Table(profile_table_name)
    table.put_item(
        Item={
            'ScanUntil': int(time.time()) + 172800,
            'ProfileName': igprofile
        }
    )
    response = table.scan(
        FilterExpression=Attr('ProfileName').eq(igprofile)
    )
    key_list = []
    for item in response["Items"]:
        key_list.append(item["ScanUntil"])
    key_list.sort()
    key_list.pop()
    for key in key_list:
        table.delete_item(
            Key={
                'ScanUntil': key,
                'ProfileName': igprofile
            }
        )


def sort_date(val):
    return val["date_found"]


def retrieve_available_stories(igprofile, count, since):
    table = dynamodb_resource.Table(story_table_name)
    response = table.query(
        KeyConditionExpression=Key('ProfileName').eq(igprofile),
        FilterExpression=Attr('FoundTime').gt(since)
    )
    story_list = []
    for item in response["Items"]:
        item_dict = {
            "url": item["StoryLocation"],
            "type": item["Type"],
            "date_found": datetime.fromtimestamp(int(item["FoundTime"])).strftime('%Y-%m-%d %H:%M:%S')
        }
        story_list.append(item_dict)
    story_list.sort(key=sort_date,reverse=True)
    if count == 0:
        return story_list
    else:
        return story_list[0:count]


def handler(event,context):
    count = 0 if "count" not in event["queryStringParameters"] else event["queryStringParameters"]["count"]
    since = int(time.time())-3600 if "since" not in event["queryStringParameters"] else event["queryStringParameters"]["since"]
    if event["queryStringParameters"] is None or "igprofile" not in event["queryStringParameters"]:
        body = "We need you to pass in an Instagram username as igprofile."
    else:
        igprofile = event["queryStringParameters"]["igprofile"]
        store_username_db(igprofile)
        stories = retrieve_available_stories(igprofile, count, int(since))
        stories.insert(0, {"total": len(stories)})
        body = json.dumps(stories)

    response = {
        "statusCode": 200,
        "headers": {
            "x-custom-header": "testing"
        },
        "body": body
    }
    return response
