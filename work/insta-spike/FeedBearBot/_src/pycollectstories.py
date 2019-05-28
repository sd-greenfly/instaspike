# ping bearbot API endpoint to ingest stories

import argparse
import base64
import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore
import codecs
import datetime
import decimal
import json
import os
import sys
import time
import uuid

try:
    import urllib.request as urllib
except ImportError:
    import urllib as urllib

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

from instagram_private_api import ClientError
from instagram_private_api import Client

script_version = "2.0"
python_version = sys.version.split(' ')[0]
s3_client = boto3.client('s3')
dynamodb_resource = boto3.resource('dynamodb')

# s3 stuff
bucket_name = "greenfly"
s3_region = "us-west-2"
environment = "dev"
story_table_name = "{}.smm.ig.stories".format(environment)
profile_table_name = "{}.smm.ig.profiles".format(environment)


def make_local_file_path_name(filename):
    path = ['/tmp', filename]
    return '/'.join(path)


def s3_upload(filename):
    s3_client.upload_file(make_local_file_path_name(filename), bucket_name, filename)
    # TODO make file public


def s3_download(filename):
    s3_resource = boto3.resource('s3')
    try:
        s3_resource.Bucket(bucket_name).download_file(filename, make_local_file_path_name(filename))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("[E] The object {0!s} does not exist on s3.".format(filename))
        else:
            raise


def get_s3_stories(user_to_check):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="stories/{}".format(user_to_check))
    results = []
    if response['KeyCount'] > 0:
        for item in response['Contents']:
            results.append(item['Key'])
    return results


def s3_story_exists(storyname, current_stories):
    if storyname in current_stories:
        return True
    return False


# login stuff


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object.get('__class__') == 'bytes':
        return codecs.decode(json_object.get('__value__').encode(), 'base64')
    return json_object


def onlogin_callback(api, settings_file):
    cache_settings = api.settings
    with open(make_local_file_path_name(settings_file), 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('[I] New auth cookie file was made: {0!s}'.format(make_local_file_path_name(settings_file)))
    s3_upload(settings_file)


def login(username="", password=""):
    device_id = None
    try:
        settings_file = "{}-credentials.json".format(username)
        local_settings_file = make_local_file_path_name(settings_file)
        s3_download(settings_file)
        if not os.path.isfile(local_settings_file):
            # settings file does not exist
            print('[W] Unable to find auth cookie file: {0!s} (creating a new one...)'.format(local_settings_file))

            # login new
            api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, settings_file))
        else:
            with open(local_settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                username, password,
                settings=cached_settings)

            print('[I] Using cached login cookie for "' + api.authenticated_user_name + '".')

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('[E] ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        if username and password:
            api = Client(
                username, password,
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, settings_file))
        else:
            print("[E] The login cookie has expired, but no login arguments were given.")
            print("[E] Please supply --username and --password arguments.")
            print('-' * 70)
            sys.exit(0)

    except ClientLoginError as e:
        print('[E] Could not login: {:s}.\n[E] {:s}\n\n{:s}'.format(
            json.loads(e.error_response).get("error_title", "Error title not available."),
            json.loads(e.error_response).get("message", "Not available"), e.error_response))
        print('-' * 70)
        sys.exit(9)
    except ClientError as e:
        print('[E] Client Error: {:s}'.format(e.error_response))
        print('-' * 70)
        sys.exit(9)
    except Exception as e:
        if str(e).startswith("unsupported pickle protocol"):
            print("[W] This cookie file is not compatible with Python {}.".format(sys.version.split(' ')[0][0]))
            print("[W] Please delete your cookie file 'credentials.json' and try again.")
        else:
            print('[E] Unexpected Exception: {0!s}'.format(e))
        print('-' * 70)
        sys.exit(99)

    print('[I] Login to "' + api.authenticated_user_name + '" OK!')
    cookie_expiry = api.cookie_jar.auth_expires
    print('[I] Login cookie expiry date: {0!s}'.format(
        datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%d at %I:%M:%S %p')))

    return api


def check_directories(user_to_check):
    try:
        if not os.path.isdir(make_local_file_path_name("stories/{}/".format(user_to_check))):
            os.makedirs(make_local_file_path_name("stories/{}/".format(user_to_check)))
        return True
    except Exception:
        return False


def create_db_entry(user_to_check, save_path_s3, type):
    table = dynamodb_resource.Table(story_table_name)
    table.put_item(
        Item={
            'ProfileName': user_to_check,
            'StoryId': str(uuid.uuid1()),
            'StoryLocation': "https://s3-{}.amazonaws.com/{}/{}".format(s3_region, bucket_name, save_path_s3),
            'FoundTime': int(time.time()),
            'Type': type
        }
    )
    print('[I] insert item succeeded')


def get_all_usernames():
    table = dynamodb_resource.Table(profile_table_name)
    response = table.scan(
        FilterExpression=Attr("ScanUntil").gt(int(time.time()))
    )
    return response['Items']


# TODO remove no_video_thumbs? or default them to True if we want them?
def get_media_story(user_to_check, user_id, ig_client, no_video_thumbs=True):
    current_stories = get_s3_stories(user_to_check)
    print("[I] got s3 story list")
    try:
        try:
            feed = ig_client.user_story_feed(user_id)
        except Exception as e:
            print("[W] An error occurred: " + str(e))
            return
        try:
            feed_json = feed['reel']['items']
            filename_feed_json = "feed_json.json"
            s3_download(filename_feed_json)
            open(make_local_file_path_name(filename_feed_json), 'w').write(json.dumps(feed_json))
            s3_upload(filename_feed_json)
        except TypeError as e:
            print("[I] There are no recent stories to process for this user.")
            return

        list_video = []
        list_image = []

        list_video_new = []
        list_image_new = []

        for media in feed_json:
            taken_ts = None

            is_video = 'video_versions' in media and 'image_versions2' in media

            if 'video_versions' in media:
                list_video.append([media['video_versions'][0]['url'], taken_ts])
            if 'image_versions2' in media:
                if (is_video and not no_video_thumbs) or not is_video:
                    list_image.append([media['image_versions2']['candidates'][0]['url'], taken_ts])

        for video in list_video:
            filename = video[0].split('/')[-1]
            final_filename = filename.split('.')[0] + ".mp4"
            save_path_s3 = "stories/{}/".format(user_to_check) + final_filename
            save_path = make_local_file_path_name(save_path_s3)

            if not s3_story_exists(save_path_s3, current_stories):
                print("[I] Downloading video: {:s}".format(final_filename))
                try:
                    urllib.urlretrieve(video[0], save_path)
                    list_video_new.append(save_path)
                    s3_upload(save_path_s3)
                    # TODO enter item into dynamodb
                    create_db_entry(user_to_check, save_path_s3, 'VIDEO')
                except Exception as e:
                    print("[W] An error occurred: " + str(e))
                    exit(1)
            else:
                print("[I] Story already exists: {:s}".format(final_filename))

        for image in list_image:
            filename = (image[0].split('/')[-1]).split('?', 1)[0]
            final_filename = filename.split('.')[0] + ".jpg"
            save_path_s3 = "stories/{}/".format(user_to_check) + final_filename
            save_path = make_local_file_path_name(save_path_s3)

            if not s3_story_exists(save_path_s3, current_stories):
                print("[I] Downloading image: {:s}".format(final_filename))
                try:
                    urllib.urlretrieve(image[0], save_path)
                    list_image_new.append(save_path)
                    s3_upload(save_path_s3)
                    # TODO enter item into dynamodb
                    create_db_entry(user_to_check, save_path_s3, 'IMAGE')
                except Exception as e:
                    print("[W] An error occurred: " + str(e))
                    exit(1)
            else:
                print("[I] Story already exists: {:s}".format(final_filename))

        if (len(list_image_new) != 0) or (len(list_video_new) != 0):
            print('-' * 70)
            print("[I] Story downloading ended with " + str(len(list_image_new)) + " new images and " + str(
                len(list_video_new)) + " new videos downloaded.")
        else:
            print('-' * 70)
            print("[I] No new stories were downloaded.")
    except Exception as e:
        print("[E] An error occurred: " + str(e))
        exit(1)
    except KeyboardInterrupt as e:
        print("[I] User aborted download.")
        exit(1)

# main program


def start():
    print("-" * 70)
    print('[I] PYINSTASTORIES (SCRIPT V{:s} - PYTHON V{:s}) - {:s}'.format(script_version, python_version,
                                                                           time.strftime('%I:%M:%S %p')))
    print("-" * 70)

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', dest='username', type=str, required=False,
                        help="Instagram username to login with.")
    parser.add_argument('-p', '--password', dest='password', type=str, required=False,
                        help="Instagram password to login with.")
    parser.add_argument('-b,', '--batch-file', dest='batchfile', type=str, required=False,
                        help="Read a text file of usernames to download stories from.")

    # Workaround to 'disable' argument abbreviations
    parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--batch-filx', help=argparse.SUPPRESS, metavar='IGNORE')

    args, unknown = parser.parse_known_args()

    if args.batchfile:
        if os.path.isfile(args.batchfile):
            users_to_check = [user.rstrip('\n') for user in open(args.batchfile)]
            if not users_to_check:
                print("[E] The specified file is empty.")
                print("-" * 70)
                sys.exit(1)
            else:
                print("[I] downloading {:d} users from batch file.".format(len(users_to_check)))
                print("-" * 70)
        else:
            print('[E] The specified file does not exist.')
            print("-" * 70)
            sys.exit(1)
    else:
        print('[E] No usernames provided. Please use the -b argument.')
        print("-" * 70)
        sys.exit(1)
# here
    if args.username and args.password:
        ig_client = login(args.username, args.password)
    else:
        settings_file = "credentials.json"
        s3_download(settings_file)
        if not os.path.isfile(make_local_file_path_name(settings_file)):
            print("[E] No username/password provided, but there is no login cookie present either.")
            print("[E] Please supply --username and --password arguments.")
            exit(1)
        else:
            ig_client = login()

    print("-" * 70)
    # TODO change this to be s3 bucket location
    print("[I] Files will be downloaded to {:s} then sent to s3".format(make_local_file_path_name("")))
    print("-" * 70)

    for index, user_to_check in enumerate(users_to_check):
        try:
            if not user_to_check.isdigit():
                user_res = ig_client.username_info(user_to_check)
                user_id = user_res['user']['pk']
            else:
                user_id = user_to_check
                user_info = ig_client.user_info(user_id)
                if not user_info.get("user", None):
                    raise Exception("No user is associated with the given user id.")
                else:
                    user_to_check = user_info.get("user").get("username")
            print("[I] Getting stories for: {:s}".format(user_to_check))
            print('-' * 70)
            if check_directories(user_to_check):
                # TODO make this match signature of method if we change it
                get_media_story(user_to_check, user_id, ig_client, False)
            else:
                print("[E] Could not make required directories. Please create a 'stories' folder manually.")
                exit(1)
            if (index + 1) != len(users_to_check):
                print('-' * 70)
                print('[I] ({}/{}) 5 second time-out until next user...'.format((index + 1), len(users_to_check)))
                time.sleep(5)
            print('-' * 70)
        except Exception as e:
            print("[E] An error occurred: " + str(e))
        except KeyboardInterrupt:
            print('-' * 70)
            print("[I] The operation was aborted.")
            exit(0)
    exit(0)


def decrypt(ciphertext):
    kms = boto3.client('kms')
    plaintext = kms.decrypt(CiphertextBlob=base64.b64decode(ciphertext))['Plaintext']
    return plaintext.decode('UTF-8')


def handler(event,context):
    message = event['Records'][0]['Sns']['Message']
    json_msg = json.loads(json.loads(message))
    users_to_check = json_msg['names']
    if len(users_to_check) == 0:
        print("[E] The table in dynamodb is empty.")
        print("-" * 70)
        sys.exit(1)
    else:
        print("[I] downloading {:d} users from dynamodb table.".format(len(users_to_check)))
        print("-" * 70)

    username_index = int(json_msg["credential_index"])
    insta_filename = "creds.json"
    if os.path.isfile(insta_filename):
        with open(insta_filename) as f:
            all_creds = json.loads(f.read())
            login_creds = all_creds[username_index]
    USERNAME = decrypt(login_creds["username"])
    PASSWORD = decrypt(login_creds["password"])
    print(USERNAME)

    if USERNAME and PASSWORD:
        ig_client = login(USERNAME, PASSWORD)
    else:
        settings_file = "credentials.json"
        s3_download(settings_file)
        if not os.path.isfile(make_local_file_path_name(settings_file)):
            print("[E] No username/password provided, but there is no login cookie present either.")
            print("[E] Please supply --username and --password arguments.")
            exit(1)
        else:
            ig_client = login()

    print("-" * 70)
    # TODO change this to be s3 bucket location
    print("[I] Files will be downloaded to {:s} then sent to s3".format(make_local_file_path_name("")))
    print("-" * 70)

    for index, user_to_check in enumerate(users_to_check):
        try:
            if not user_to_check.isdigit():
                user_res = ig_client.username_info(user_to_check)
                user_id = user_res['user']['pk']
            else:
                user_id = user_to_check
                user_info = ig_client.user_info(user_id)
                if not user_info.get("user", None):
                    raise Exception("No user is associated with the given user id.")
                else:
                    user_to_check = user_info.get("user").get("username")
            print("[I] Getting stories for: {:s}".format(user_to_check))
            print('-' * 70)
            if check_directories(user_to_check):
                # TODO make this match signature of method if we change it
                get_media_story(user_to_check, user_id, ig_client, True)
            else:
                print("[E] Could not make required directories. Please create a 'stories' folder manually.")
                exit(1)
            if (index + 1) != len(users_to_check):
                print('-' * 70)
                print('[I] ({}/{}) 2 second time-out until next user...'.format((index + 1), len(users_to_check)))
                time.sleep(2)
            print('-' * 70)
        except Exception as e:
            print("[E] An error occurred: " + str(e))
        except KeyboardInterrupt:
            print('-' * 70)
            print("[I] The operation was aborted.")
            exit(0)
    print("[I] ------ script is done ------")
    return "Completed checking {} users".format(len(users_to_check))