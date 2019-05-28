To install all this stuff.

1. Install Python 3.7.3
2. Configure awscli to use your desired aws account
3. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)

In FeedBearBot directory
1. modify gen_tables.py to use info for your account (region_name and environment prefix)
2. python3 gen_tables.py (creates dynamodb tables)
3. modify _src/creds.json to be encoded with your KMS key and your username/password combo for testing (see README in FeedBearBot)
4. kappa deploy (creates lambda function, gives permissions to dynamodb, s3)

In GateKeeper directory
1. kappa deploy (creates lambda function, gives permissions to dynamodb)
2. modify gen_api_gateway.py for your account (region, aws_account_identifier, lambda name from step Gatekeeper.1, environment prefix)
3. python3 gen_api_gateway.py (creates api gateway access to script, adds permission to lambda in Gatekeeper.1)

In FannerOuter
1. kappa deploy (creates lambda function, gives permissions to dynamodb)
2. modify create_sns_topic.py for your account (region, aws_account_identifier, lambda name from FeedBearBot.4)
3. python3 create_sns_topic.py (creates sns topic, adds permission to lambda in FeedBearBot.4 to be triggered by & subscribes FeedBearBot.4 lambda to sns topic)
