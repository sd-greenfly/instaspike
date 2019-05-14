import boto3

region = "us-west-2"
aws_account_identifier="968765799102"
lambda_arn = "arn:aws:lambda:{}:{}:function:gatekeeper".format(region,aws_account_identifier)
gateway_name = "smmgateway"
environment="dev"

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

# add permission to lambda function
lambda_client = boto3.client('lambda')
response = lambda_client.add_permission(
    FunctionName='gatekeeper',
    StatementId='bar',
    Action='lambda:InvokeFunction',
    Principal='apigateway.amazonaws.com',
    SourceArn="arn:aws:execute-api:{}:{}:{}/*/*/{}".format(region,aws_account_identifier,rest_api_id,gateway_name)
)
