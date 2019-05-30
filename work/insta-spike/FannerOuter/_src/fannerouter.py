import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import os
import time

# configurations from file
config_filename = "configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"
region = all_configs['region'] if 'region' in all_configs.keys() else "us-west-2"
aws_account_identifier = all_configs['aws_account_identifier'] if 'aws_account_identifier' in all_configs.keys() else "968765799102"
sns_topic = all_configs['sns_topic'] if 'sns_topic' in all_configs.keys() else "smmigfan"

topic_arn = "arn:aws:sns:{}:{}:{}-{}".format(region, aws_account_identifier, environment, sns_topic)

dynamodb_resource = boto3.resource('dynamodb')
profile_table_name = "{}.smm.ig.profiles".format(environment)
credential_table_name = "{}.smm.ig.credentials".format(environment)
sns = boto3.resource('sns')
topic = sns.Topic(topic_arn)


def get_all_usernames():
    table = dynamodb_resource.Table(profile_table_name)
    response = table.scan(
        FilterExpression=Attr("ScanUntil").gt(int(time.time()))
    )
    return response['Items']


def get_all_credentials():
    table = dynamodb_resource.Table(credential_table_name)
    response = table.scan()
    return response['Items']


def get_number_shards(list_size, shard_size):
    if list_size == 0:
        print("no users to scan currently")
        num_shards = 0
        exit(0)
    elif list_size <= shard_size:
        print("one shard only")
        num_shards = 1
    else:
        num_shards = list_size//shard_size
        if list_size%shard_size > 0:
            num_shards += 1
    return num_shards


def send_users(user_list, credential_name):
    msg = {"credential_name": credential_name, "names": user_list}
    response = topic.publish(
        Message=json.dumps(json.dumps(msg))
    )


def handler(event, context):
    # get list of accounts to scan from profile table
    users_to_check = []
    credentials_to_use = []
    shard_size = 2
    for item in get_all_usernames():
        users_to_check.append(item['ProfileName'])
    total_shards = get_number_shards(len(users_to_check), shard_size)
    for item in get_all_credentials():
        credentials_to_use.append(item['ProfileName'])
    if total_shards == 1:
        send_users(users_to_check, credentials_to_use[0])
    else:
        for x in range(total_shards):
            shard_users = users_to_check[x*shard_size:((x+1)*shard_size)]
            send_users(shard_users, credentials_to_use[x % len(credentials_to_use)])
