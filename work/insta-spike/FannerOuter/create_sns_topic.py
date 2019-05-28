import boto3

region = "us-west-2"
aws_identifier = "968765799102"
scraper_lambda_name = "insta-spike"
arn_scraper = "arn:aws:lambda:{}:{}:function:{}".format(region, aws_identifier, scraper_lambda_name)
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