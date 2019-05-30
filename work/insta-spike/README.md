# To install all this stuff.

1. Install Python 3.7.3
2. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)
3. Create user for aws account with administrator level access.
4. Configure awscli to use your desired aws account & user.
5. Checkout all code

### In `FeedBearBot` directory
1. modify `gen_tables.py` to use info for your account 
   - region_name
   - environment -- if you change the environment prefix, change it also in
     - FeedBearBot.6
     - GateKeeper.1
     - FannerOuter.3
2. `python3 gen_tables.py` 
   - creates dynamodb tables
3. modify `create_kms_key.py` to use info for your account 
   - region
   - aws_account_identifier
   - environment
   - key_alias (currently alias/robo-greenfly -- it must take the form of "alias/<whatever you want>")
   - user_arn
4. `python3 create_kms_key.py` to create your KMS key.
5. `python3 encrypt_ig_credentials.py -k <key_alias> -u <IGusername> -p <IGpassword>`
   - This will encrypt the username & password and put them into a dynamodb table for use by lambda functions
6. modify `_src/pycollectstories.py` for your account
   - bucket_name
   - s3_region
   - environment (match FeedBearBot.1)
7. modify `kappa.yml` to your 
   - aws account -- currently sarah's personal 
     - line 14
     - line 18
   - region -- currently us-west-2 
     - line 6
     - line 14
     - line 18
   - desired lambda function name -- currently insta-spike 
     - line 2
     - line 18
     - line 102 **must match** name of file in codebase
8. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, read/write s3, run lambda function
9. `kappa invoke _tests/test_sns_input.json` 
   - this will run the lambda using the 1st account in the `_src/creds.json` file, to retrieve the stories from 
   the nba & nfl instagram accounts, storing any results in s3 and the dynamodb tables

### In `GateKeeper` directory
1. modify `_src/gatekeeper.py` for your account 
   - environment (match FeedBearBot.1)
2. modify `kappa.yml` to your 
   - aws account -- currently sarah's personal 
     - line 10
     - line 14
   - region -- currently us-west-2 
     - line 6
     - line 10
     - line 14
   - desired lambda function name -- currently gatekeeper
     - line 2
     - line 14
     - line 94 **must match** name of file in codebase
3. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, run lambda function
4. `kappa invoke _tests/test_nfl.json` 
   - simulates hitting the lambda function with an event requesting stories from the nfl instagram account
5. modify `gen_api_gateway.py` for your account
   - region
   - aws_account_identifier
   - lambda name from GateKeeper.3
   - environment prefix (match FeedBearBot.1)
6. `python3 gen_api_gateway.py` 
   - creates api gateway access to script, adds permission to lambda in GateKeeper.3
7. `aws apigateway get-rest-apis` 
   - should retrieve info on the just generated API gateway
8. Visit `https://<id>.execute-api.<region>.amazonaws.com/dev/<name>?igprofile=nfl` in a browser substituting 
   - id from GateKeeper.7
   - name from GateKeeper.7
   - region you used in GateKeeper.5

### In `FannerOuter` directory
1. modify `create_sns_topic.py` for your account
   - region
   - aws_account_identifier
   - lambda name from FeedBearBot.8
   - sns_topic_name
2. `python3 create_sns_topic.py` 
   - creates sns topic, adds permission to lambda in FeedBearBot.8 to be triggered by & 
   subscribes FeedBearBot.8 lambda to sns topic)
3. modify `_src/fannerouter.py` for your account
   - topic_arn from FannerOuter.2
   - environment from FeedBearBot.7
4. modify `kappa.yml` to your
   - aws account -- currently sarah's personal 
     - line 10
     - line 14
   - region -- currently us-west-2 
     - line 6
     - line 10
     - line 14
   - desired lambda function name -- currently fannerouter
     - line 2
     - line 14
     - line 95 **must match** name of file in codebase
5. `kappa deploy`
   - creates lambda function, gives permissions to dynamodb
6. `kappa invoke _tests/test-blank.json`
   - this will kick the script to query the dynamodb profiles table to find which instagram accounts to query, 
   shard it with 2 accounts per shard, and send messages to the sns topic which the lambda from FeedBearBot.8 
   is subscribed to. 
   - You can observe logs from that lambda running in your CloudWatch log group
     - `https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logStream:group=/aws/lambda/insta-spike;streamFilter=typeLogStreamPrefix`
       - substitute region 
       - substitute FeedBearBot.8 lambda name
