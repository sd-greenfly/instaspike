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
gateway_lambda_name = all_configs['gateway_lambda_name'] if 'gateway_lambda_name' in all_configs.keys() else "gatekeeper"
gateway_name = all_configs['gateway_api_name'] if 'gateway_api_name' in all_configs.keys() else "smmgateway"

lambda_arn = "arn:aws:lambda:{}:{}:function:{}".format(region, aws_account_identifier, gateway_lambda_name)

client = boto3.client('apigateway')

# make the api gateway rest api (could be named different than gateway_name used for path, but used same for ease)
# REGIONAL choice to keep it lower for billing purposes, we could choose differently if we want
response = client.create_rest_api(
    name=gateway_name,
    endpointConfiguration={
        'types': ['REGIONAL']
    }
)
rest_api_id = response['id']
print("rest api id is {}".format(rest_api_id))

# get the id for the / url in the rest api
response = client.get_resources(
    restApiId=rest_api_id
)
parent_id = response['items'][0]['id']

# make the path you want to call the rest api at (gateway_name)
response = client.create_resource(
    restApiId=rest_api_id,
    parentId=parent_id,
    pathPart=gateway_name
)
resource_id = response['id']

# make a method for that endpoint to respond to -- can change this to httpMethod='GET' in future for security?
response = client.put_method(
    restApiId=rest_api_id,
    resourceId=resource_id,
    httpMethod='ANY',
    authorizationType='NONE'
)

# tie this endpoint to the lambda function -- integrationHttpMethod is required, and it must be POST
response = client.put_integration(
    restApiId=rest_api_id,
    resourceId=resource_id,
    httpMethod='ANY',
    type='AWS_PROXY',
    uri="arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations".format(region,lambda_arn),
    integrationHttpMethod='POST'
)

# deploy the API to make it web accessible
response = client.create_deployment(
    restApiId=rest_api_id,
    stageName=environment
)

# add permission for apiGateway to invoke lambda function
lambda_client = boto3.client('lambda')
response = lambda_client.add_permission(
    FunctionName='gatekeeper',
    StatementId='bar',
    Action='lambda:InvokeFunction',
    Principal='apigateway.amazonaws.com',
    SourceArn="arn:aws:execute-api:{}:{}:{}/*/*/{}".format(region,aws_account_identifier,rest_api_id,gateway_name)
)
