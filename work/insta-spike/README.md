To install all this stuff.

1. Install Python 3.7.3
2. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)
3. Create user for aws account with administrator level access.
4. Configure awscli to use your desired aws account & user.

In FeedBearBot directory
1. modify FeedBearBot/create_kms_key.py to use info for your account (region, aws_account_identifier, environment, 
key_alias (currently alias/robo-greenfly -- it must take the form of "alias/<whatever you want>"), user_arn)
2. (command-line> python3 create_kms_key.py) to create your KMS key.
3. Encode your Instagram account(s) IGusername & IGpassword 
(command-line> aws kms encrypt --key-id alias/robo-greenfly --plaintext IGusername --output text) 
and place in FeedBearBot/_src/creds.json
4. modify gen_tables.py to use info for your account (region_name, environment -- if you change the environment prefix,
change it also in FeedBearBot/_src/pycollectstories.py, GateKeeper/_src/gatekeeper.py, FannerOuter/_src/fannerouter.py)
5. (command-line> python3 gen_tables.py) (creates dynamodb tables)
6. modify kappa.yml to your aws account (currently sarah's personal ll 14, 18), 
region (currently us-west-2 ll 6, 14, 18), and 
desired lambda function name (currently insta-spike ll 2, 18 -- l 102 must match name of file in codebase)
7. (command-line> kappa deploy) (creates lambda function, gives permissions to dynamodb, s3)

In GateKeeper directory
1. modify kappa.yml to your aws account (currently sarah's personal ll 10, 14), 
region (currently us-west-2 ll 6, 10,14), and 
desired lambda function name (currently 'gatekeeper' ll 2, 14 -- l 94 must match name of file in codebase)
2. (command-line> kappa deploy) (creates lambda function, gives permissions to dynamodb)
3. modify gen_api_gateway.py for your account (region, aws_account_identifier, lambda name from step GateKeeper.1, 
environment prefix)
4. (command-line> python3 gen_api_gateway.py) (creates api gateway access to script, adds permission to lambda in 
GateKeeper.1)

In FannerOuter
1. modify kappa.yml to your aws account (currently sarah's personal ll 10, 14), 
region (currently us-west-2 ll 6, 10, 14),and 
desired lambda function name (currently fannerouter ll 2, 14 -- l 95 must match name of file in codebase)
2. (command-line> kappa deploy) (creates lambda function, gives permissions to dynamodb)
3. modify create_sns_topic.py for your account (region, aws_account_identifier, lambda name from FeedBearBot.6, 
sns_topic_name)
4. (command-line> python3 create_sns_topic.py) (creates sns topic, adds permission to lambda in FeedBearBot.6 to be 
triggered by & subscribes FeedBearBot.6 lambda to sns topic)
