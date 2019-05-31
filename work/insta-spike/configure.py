from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import json
import os
import subprocess

# configurations from file
config_filename = "FeedBearBot/_src/configs.json"
if os.path.isfile(config_filename):
    with open(config_filename) as f:
        all_configs = json.loads(f.read())
environment = all_configs['environment'] if 'environment' in all_configs.keys() else "dev"
region = all_configs['region'] if 'region' in all_configs.keys() else "us-west-2"
aws_account_identifier = all_configs['aws_account_identifier'] if 'aws_account_identifier' in all_configs.keys() else "968765799102"
# key_alias = all_configs['key_alias'] if 'key_alias' in all_configs.keys() else "alias/robo-greenfly"
# key_user = all_configs['key_user'] if 'key_user' in all_configs.keys() else "sd-greenfly"

print("Starting modification of FeedBearBot kappa.yml file")
print("-"*70)
stream = open('FeedBearBot/kappa_template.yml', 'r')
data = load(stream, Loader=Loader)
feed_lambda_name = all_configs['scraper_lambda_name'] if 'scraper_lambda_name' in all_configs.keys() else exit(1)
data['name'] = feed_lambda_name
for x in data['environments']['dev']['policy']['statements']:
    if x['Resource'] == "LogGroup":
        x['Resource'] = "arn:aws:logs:{}:{}:*".format(region, aws_account_identifier)
    if x['Resource'] == "LogStream":
        x['Resource'] = "arn:aws:logs:{}:{}:log-group:/aws/lambda/{}:*".format(region, aws_account_identifier, feed_lambda_name)
data['environments']['dev']['region'] = region
stream = open('FeedBearBot/kappa.yml', 'w')
dump(data, stream=stream, Dumper=Dumper, explicit_start=True)
print("Completed modification of FeedBearBot kappa.yml file")
print("-"*70)

status = subprocess.call('cp FeedBearBot/_src/configs.json GateKeeper/_src/configs.json', shell=True)

print("Starting modification of GateKeeper kappa.yml file")
print("-"*70)
stream = open('GateKeeper/kappa_template.yml', 'r')
data = load(stream, Loader=Loader)
gate_lambda_name = all_configs['gateway_lambda_name'] if 'gateway_lambda_name' in all_configs.keys() else exit(1)
data['name'] = gate_lambda_name
for x in data['environments']['dev']['policy']['statements']:
    if x['Resource'] == "LogGroup":
        x['Resource'] = "arn:aws:logs:{}:{}:*".format(region, aws_account_identifier)
    if x['Resource'] == "LogStream":
        x['Resource'] = "arn:aws:logs:{}:{}:log-group:/aws/lambda/{}:*".format(region, aws_account_identifier, gate_lambda_name)
data['environments']['dev']['region'] = region
stream = open('GateKeeper/kappa.yml', 'w')
dump(data, stream=stream, Dumper=Dumper, explicit_start=True)
print("Completed modification of GateKeeper kappa.yml file")
print("-"*70)

status = subprocess.call('cp FeedBearBot/_src/configs.json FannerOuter/_src/configs.json', shell=True)

print("Starting modification of FannerOuter kappa.yml file")
print("-"*70)
stream = open('FannerOuter/kappa_template.yml', 'r')
data = load(stream, Loader=Loader)
fan_lambda_name = all_configs['fanner_lambda_name'] if 'fanner_lambda_name' in all_configs.keys() else exit(1)
data['name'] = fan_lambda_name
for x in data['environments']['dev']['policy']['statements']:
    if x['Resource'] == "LogGroup":
        x['Resource'] = "arn:aws:logs:{}:{}:*".format(region, aws_account_identifier)
    if x['Resource'] == "LogStream":
        x['Resource'] = "arn:aws:logs:{}:{}:log-group:/aws/lambda/{}:*".format(region, aws_account_identifier, fan_lambda_name)
data['environments']['dev']['region'] = region
stream = open('FannerOuter/kappa.yml', 'w')
dump(data, stream=stream, Dumper=Dumper, explicit_start=True)
print("Completed modification of FannerOuter kappa.yml file")
print("-"*70)
