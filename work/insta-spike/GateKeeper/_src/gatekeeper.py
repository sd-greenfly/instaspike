def handler(event,context):
    response = {
        "statusCode": 200,
        "headers": {
            "x-custom-header" : "testing"
        },
        "body": "Hello {}".format(event["queryStringParameters"]["name"])
    }
    return response
