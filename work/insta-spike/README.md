To install all this stuff.

1. Install Python 3.7.3
2. Configure awscli to use your desired aws account
3. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)
3. in FeedBearBot directory
3.1 modify gen_tables.py to use info for your account (region_name and environment prefix)
3.2 python3 gen_tables.py (creates dynamodb tables)
3.3 kappa deploy (creates lambda function, gives permissions to dynamodb, s3)
4. in GateKeeper directory
4.1 kappa deploy (creates lambda function, gives permissions to dynamodb)
4.2 modify gen_api_gateway.py for your account (region, aws_account_identifier, lambda name from step 4.1, environment prefix)
4.3 python3 gen_api_gateway.py (creates api gateway access to script, adds permission to lambda in 4.1)
5. in FannerOuter
5.1 kappa deploy (creates lambda function, gives permissions to dynamodb)
5.2 modify create_sns_topic.py for your account (region, aws_account_identifier, lambda name from 3.3)
5.2 python3 create_sns_topic.py (creates sns topic, adds permission to lambda in 3.3 to be triggered by & subscribes 3.3 lambda to sns topic)
