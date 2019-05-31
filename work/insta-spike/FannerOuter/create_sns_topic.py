import boto3
import json
import os

# configurations from file
config_filename = "_src/configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"
region = all_configs['region'] if 'region' in all_configs.keys() else "us-west-2"
aws_account_identifier = all_configs['aws_account_identifier'] if 'aws_account_identifier' in all_configs.keys() else "968765799102"
scraper_lambda_name = all_configs['scraper_lambda_name'] if 'scraper_lambda_name' in all_configs.keys() else "insta-spike"
sns_topic = all_configs['sns_topic'] if 'sns_topic' in all_configs.keys() else "smmigfan"

arn_scraper = "arn:aws:lambda:{}:{}:function:{}".format(region, aws_account_identifier, scraper_lambda_name)
sns_topic_name = "{}-{}".format(environment, sns_topic)

sns = boto3.resource('sns')

topic = sns.create_topic(
    Name=sns_topic_name
)

# add permission to lambda function
lambda_client = boto3.client('lambda')
response = lambda_client.add_permission(
    FunctionName=arn_scraper,
    StatementId="{}-fanout".format(environment),
    Action='lambda:InvokeFunction',
    Principal='sns.amazonaws.com',
    SourceArn=topic.arn
)

subscription = topic.subscribe(
    Protocol="lambda",
    Endpoint=arn_scraper
)

print("Subscription complete: {}".format(subscription))
