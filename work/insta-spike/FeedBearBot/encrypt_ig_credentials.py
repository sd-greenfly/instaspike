import argparse
import base64
import boto3
import sys
import uuid

region = "us-west-2"
aws_account_identifier = "968765799102"
environment = 'dev'
credential_table_name = "{}.smm.ig.credentials".format(environment)

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
kms_client = boto3.client('kms')


def encrypt(plaintext, keyalias):
    response = kms_client.encrypt(
        KeyId=keyalias,
        Plaintext=plaintext.encode('UTF-8'),
    )
    return base64.b64encode(response['CiphertextBlob']).decode('UTF-8')


def check_alias_exists(keyalias):
    response = kms_client.list_aliases()
    for alias in response['Aliases']:
        if alias['AliasName'] == keyalias:
            return True
    return False


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', dest='username', type=str, required=False,
                        help="Instagram username to login with.")
    parser.add_argument('-p', '--password', dest='password', type=str, required=False,
                        help="Instagram password to login with.")
    parser.add_argument('-k,', '--key-alias', dest='keyalias', type=str, required=False,
                        help="AWS KMS key alias to use to encrypt.")

    # Workaround to 'disable' argument abbreviations
    parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--key-aliax', help=argparse.SUPPRESS, metavar='IGNORE')

    args, unknown = parser.parse_known_args()

    if args.keyalias:
        if check_alias_exists(args.keyalias):
            print("[I] key alias is valid. Continuing.")
        else:
            print('[E] Bad key alias provided. Please verify correct alias to use with the -k argument.')
            print("-" * 70)
            sys.exit(1)
    else:
        print('[E] No key alias provided. Please use the -k argument.')
        print("-" * 70)
        sys.exit(1)

    if args.username and args.password:
        username_encrypted = encrypt(args.username, args.keyalias)
        password_encrypted = encrypt(args.password, args.keyalias)

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
