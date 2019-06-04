# To install all this stuff.

1. Install Python 3.7.3
2. Enable aws account access to dynamodb, lambda, s3 (I did this in web interface, not scripted)
3. Create user for aws account with administrator level access.
4. Create s3 bucket for storing downloaded stories.
5. Configure awscli to use your desired aws account & user.
6. `pip3 install kappa`
7. Checkout all code
8. modify `FeedBearBot/_src/configs.json` to use info for your account
9. `python3 configure.py` from inside the base code directory. (It uses relative locations)

### In `FeedBearBot` directory
1. `python3 gen_tables.py` 
   - creates dynamodb tables
2. `python3 create_kms_key.py` to create your KMS key.
3. `python3 encrypt_ig_credentials.py -u <IGusername> -p <IGpassword>`
   - This will encrypt the username & password and put them into a dynamodb table for use by lambda functions
4. modify `kappa.yml` to your 
   - environment -- currently `dev` (**must match** `environment` in `_src/configs.json`)
5. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, read/write s3, run lambda function
   - if you modified the environment name in FeedBearBot.4, you need to run `kappa deploy --env <environment>`
6. modify `_tests/test_sns_input.json` to have the username of your test instagram account from FeedBearBot.3
7. `kappa invoke _tests/test_sns_input.json` 
   - this will run the lambda using the account in FeedBearBot.3, to retrieve the stories from 
   the nba & nfl instagram accounts, storing any results in s3 and the dynamodb tables
   - this test will take a while the first time you run it, as it is downloading and uploading things. 

### In `GateKeeper` directory
1. modify `kappa.yml` to your 
   - environment -- currently `dev` (**must match** `environment` in `_src/configs.json`)
2. `kappa deploy` 
   - creates lambda function, gives permissions to read/write dynamodb, run lambda function
   - if you modified the environment name in step 1, you need to run `kappa deploy --env <environment>`
3. `kappa invoke _tests/test_nfl.json` 
   - simulates hitting the lambda function with an event requesting stories from the nfl instagram account
4. `python3 gen_api_gateway.py` 
   - creates api gateway access to script, adds permission to lambda in GateKeeper.2
5. `aws apigateway get-rest-apis` 
   - should retrieve info on the just generated API gateway
6. Visit `https://<id>.execute-api.<region>.amazonaws.com/dev/<name>?igprofile=nfl` in a browser substituting 
   - id from GateKeeper.5
   - name from GateKeeper.5
   - region you used in `_src/configs.json`
   - change "nfl" in the url to other instagram accounts, to add more accounts for the scripts to watch and get 
   stories from.

### In `FannerOuter` directory
1. `python3 create_sns_topic.py` 
   - creates sns topic, adds permission to `_src/configs.json` `scraper_lambda_name` lambda to be triggered by sns & 
   subscribes `_src/configs.json` `scraper_lambda_name` lambda to sns topic)
2. modify `kappa.yml` to your
   - environment -- currently `dev` (**must match** `environment` in `_src/configs.json`)
3. `kappa deploy`
   - creates lambda function, gives permissions to dynamodb
   - if you modified the environment name in step 2, you need to run `kappa deploy --env <environment>`
4. `kappa invoke _tests/test-blank.json`
   - this will kick the script to query the dynamodb profiles table to find which instagram accounts to query, 
   shard it with 2 accounts per shard, and send messages to the sns topic which the `_src/configs.json` 
   `scraper_lambda_name` lambda is subscribed to. 
     - the more accounts you have hit in GateKeeper.6, the more shards you will get.
   - You can observe logs from that lambda running in your CloudWatch log group
     - `https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logStream:group=/aws/lambda/insta-spike;streamFilter=typeLogStreamPrefix`
       - substitute `_src/configs.json` `region`
       - substitute `_src/configs.json` `scraper_lambda_name`
