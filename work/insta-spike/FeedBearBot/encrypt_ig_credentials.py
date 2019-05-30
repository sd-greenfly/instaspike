import argparse
import base64
import boto3
import json
import os
import sys
import uuid


# configurations from file
config_filename = "_src/configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"
region = all_configs['region'] if 'region' in all_configs.keys() else "us-west-2"
aws_account_identifier = all_configs['aws_account_identifier'] if 'aws_account_identifier' in all_configs.keys() else "968765799102"
key_alias = all_configs['key_alias'] if 'key_alias' in all_configs.keys() else "alias/robo-greenfly"

credential_table_name = "{}.smm.ig.credentials".format(environment)

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
kms_client = boto3.client('kms')


def encrypt(plaintext):
    response = kms_client.encrypt(
        KeyId=key_alias,
        Plaintext=plaintext.encode('UTF-8'),
    )
    return base64.b64encode(response['CiphertextBlob']).decode('UTF-8')


def check_alias_exists():
    response = kms_client.list_aliases()
    for alias in response['Aliases']:
        if alias['AliasName'] == key_alias:
            return True
    return False


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', dest='username', type=str, required=False,
                        help="Instagram username to login with.")
    parser.add_argument('-p', '--password', dest='password', type=str, required=False,
                        help="Instagram password to login with.")

    # Workaround to 'disable' argument abbreviations
    parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')

    args, unknown = parser.parse_known_args()

    if check_alias_exists():
        print("[I] key alias is valid. Continuing.")
    else:
        print('[E] Bad key alias provided in _src/configs.json. Please verify correct alias.')
        print("-" * 70)
        sys.exit(1)

    if args.username and args.password:
        username_encrypted = encrypt(args.username)
        password_encrypted = encrypt(args.password)

        table = dynamodb_resource.Table(credential_table_name)
        table.put_item(
            Item={
                'ProfileName': args.username,
                'ProfileId': str(uuid.uuid1()),
                'Username': username_encrypted,
                'Password': password_encrypted
            }
        )
        print('[I] insert item succeeded')
    else:
        print('[E] missing username or password. Please use the -u and -p arguments.')
        print("-" * 70)
        sys.exit(1)
    print('[I] all done!')
    exit(0)


main()
