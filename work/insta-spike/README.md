# To install all this stuff.

1. Install Python 3.7.3
2. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)
3. Create user for aws account with administrator level access.
4. Create s3 bucket for storing downloaded stories.
5. Configure awscli to use your desired aws account & user.
6. Checkout all code

### In `FeedBearBot` directory
1. modify `_src/configs.json` to use info for your account
2. `python3 gen_tables.py` 
   - creates dynamodb tables
3. `python3 create_kms_key.py` to create your KMS key.
4. `python3 encrypt_ig_credentials.py -u <IGusername> -p <IGpassword>`
   - This will encrypt the username & password and put them into a dynamodb table for use by lambda functions
5. modify `kappa.yml` to your 
   - aws account -- currently sarah's personal (**must match** `aws_account_identifier` in `_src/configs.json`)
     - line 14
     - line 18
   - region -- currently us-west-2 (**must match** `region` in `_src/configs.json`)
     - line 6
     - line 14
     - line 18
   - desired lambda function name -- currently insta-spike (**must match** `scraper_lambda_name` in `_src/configs.json`)
     - line 2
     - line 18
     - line 102 **must match** name of file in codebase
6. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, read/write s3, run lambda function
7. modify `_tests/test_sns_input.json` to have the username of your test instagram account from FeedBearBot.4
8. `kappa invoke _tests/test_sns_input.json` 
   - this will run the lambda using the account in FeedBearBot.7, to retrieve the stories from 
   the nba & nfl instagram accounts, storing any results in s3 and the dynamodb tables

### In `GateKeeper` directory
1. `cp ../FeedBearBot/_src/configs.json _src/configs.json`
2. modify `kappa.yml` to your 
   - aws account -- currently sarah's personal (**must match** `aws_account_identifier` in `_src/configs.json`)
     - line 10
     - line 14
   - region -- currently us-west-2 (**must match** `region` in `_src/configs.json`)
     - line 6
     - line 10
     - line 14
   - desired lambda function name -- currently gatekeeper (**must match** `gateway_lambda_name` in `_src/configs.json`)
     - line 2
     - line 14
     - line 94 **must match** name of file in codebase
3. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, run lambda function
4. `kappa invoke _tests/test_nfl.json` 
   - simulates hitting the lambda function with an event requesting stories from the nfl instagram account
5. `python3 gen_api_gateway.py` 
   - creates api gateway access to script, adds permission to lambda in GateKeeper.3
6. `aws apigateway get-rest-apis` 
   - should retrieve info on the just generated API gateway
7. Visit `https://<id>.execute-api.<region>.amazonaws.com/dev/<name>?igprofile=nfl` in a browser substituting 
   - id from GateKeeper.6
   - name from GateKeeper.6
   - region you used in `_src/configs.json`

### In `FannerOuter` directory
1. `cp ../FeedBearBot/_src/configs.json _src/configs.json`
2. `python3 create_sns_topic.py` 
   - creates sns topic, adds permission to `_src/configs.json` `scraper_lambda_name` lambda to be triggered by sns & 
   subscribes `_src/configs.json` `scraper_lambda_name` lambda to sns topic)
3. modify `kappa.yml` to your
   - aws account -- currently sarah's personal (**must match** `aws_account_identifier` in `_src/configs.json`)
     - line 10
     - line 14
   - region -- currently us-west-2 (**must match** `region` in `_src/configs.json`)
     - line 6
     - line 10
     - line 14
   - desired lambda function name -- currently fannerouter (**must match** `fanner_lambda_name` in `_src/configs.json`)
     - line 2
     - line 14
     - line 95 **must match** name of file in codebase
4. `kappa deploy`
   - creates lambda function, gives permissions to dynamodb
5. `kappa invoke _tests/test-blank.json`
   - this will kick the script to query the dynamodb profiles table to find which instagram accounts to query, 
   shard it with 2 accounts per shard, and send messages to the sns topic which the `_src/configs.json` 
   `scraper_lambda_name` lambda is subscribed to. 
   - You can observe logs from that lambda running in your CloudWatch log group
     - `https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logStream:group=/aws/lambda/insta-spike;streamFilter=typeLogStreamPrefix`
       - substitute `_src/configs.json` `region`
       - substitute `_src/configs.json` `scraper_lambda_name`
