import boto3

arn_scraper = "arn:aws:lambda:us-west-2:968765799102:function:insta-spike"
sns = boto3.resource('sns')

topic = sns.create_topic(
    Name="smmigfan"
)

# add permission to lambda function
lambda_client = boto3.client('lambda')
response = lambda_client.add_permission(
    FunctionName=arn_scraper,
    StatementId='fanout',
    Action='lambda:InvokeFunction',
    Principal='sns.amazonaws.com',
    SourceArn=topic.arn
)

subscription = topic.subscribe(
    Protocol="lambda",
    Endpoint=arn_scraper
)

print("Subscription complete: {}".format(subscription))