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
key_alias = all_configs['key_alias'] if 'key_alias' in all_configs.keys() else "alias/robo-greenfly"
key_user = all_configs['key_user'] if 'key_user' in all_configs.keys() else "sd-greenfly"

user_arn = "arn:aws:iam::{}:user/{}".format(aws_account_identifier, key_user)

# generate KMS key

kms_client = boto3.client('kms')
response = kms_client.create_key(
    Description='greenfly',
    KeyUsage='ENCRYPT_DECRYPT',
    Origin='AWS_KMS'
)

print(response)
key_id = response['KeyMetadata']['KeyId']

response = kms_client.create_alias(
    AliasName=key_alias,
    TargetKeyId=key_id
)
print(response)

# assign administration & usage of key to this user

policy = ("{\n  \"Version\" : \"2012-10-17\",\n  \"Id\" : \"key-consolepolicy-3\",\n  "
          "\"Statement\" : [ {\n    \"Sid\" : \"Enable IAM User Permissions\",\n    \"Effect\" : \"Allow\",\n    "
          "\"Principal\" : {\n      \"AWS\" : \"arn:aws:iam::"+aws_account_identifier+":root\"\n    },\n    "
          "\"Action\" : \"kms:*\",\n    \"Resource\" : \"*\"\n  }, "
          "{\n    \"Sid\" : \"Allow access for Key Administrators\",\n    \"Effect\" : \"Allow\",\n    "
          "\"Principal\" : {\n      \"AWS\" : \""+user_arn+"\"\n    },\n    "
          "\"Action\" : [ \"kms:Create*\", \"kms:Describe*\", \"kms:Enable*\", \"kms:List*\", \"kms:Put*\", "
          "\"kms:Update*\", \"kms:Revoke*\", \"kms:Disable*\", \"kms:Get*\", \"kms:Delete*\", \"kms:TagResource\", "
          "\"kms:UntagResource\", \"kms:ScheduleKeyDeletion\", \"kms:CancelKeyDeletion\" ],\n    "
          "\"Resource\" : \"*\"\n  }, {\n    \"Sid\" : \"Allow use of the key\",\n    \"Effect\" : \"Allow\",\n    "
          "\"Principal\" : {\n      \"AWS\" : \""+user_arn+"\"\n    },\n    "
          "\"Action\" : [ \"kms:Encrypt\", \"kms:Decrypt\", \"kms:ReEncrypt*\", \"kms:GenerateDataKey*\", "
          "\"kms:DescribeKey\" ],\n    \"Resource\" : \"*\"\n  }, "
          "{\n    \"Sid\" : \"Allow attachment of persistent resources\",\n    "
          "\"Effect\" : \"Allow\",\n    \"Principal\" : {\n      \"AWS\" : \""+user_arn+"\"\n    "
          "},\n    \"Action\" : [ \"kms:CreateGrant\", \"kms:ListGrants\", \"kms:RevokeGrant\" ],\n    "
          "\"Resource\" : \"*\",\n    \"Condition\" : {\n      \"Bool\" : {\n        "
          "\"kms:GrantIsForAWSResource\" : \"true\"\n      }\n    }\n  } ]\n}")

response = kms_client.put_key_policy(
    KeyId=key_id,
    PolicyName='default',
    Policy=policy
)
# print alias assigned

print(response)
