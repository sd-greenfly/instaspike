This script is heavily cribbed from PyInstaStories -- some options have been removed, and boto3 AWS S3 integration has been added.

Steps I took to make it function on my MBP.



1. Install Python 3.7.3
2. use pip3 to install https://github.com/ping/instagram_private_api
3. run  /Applications/Python\ 3.7/Install\ Certificates.command
-- now program can successfully complete login.
4. install awscli using pip3
5. configure awscli -- used my personal s3 account on region: us-west-2

Encrypt instagram credentials

1. Create an encryption key in AWS console for KMS administrated by user awscli is configured for. (not scripted currently)
2. aws kms encrypt --key-id alias/keyname --plaintext username --output text
3. put this value into creds.json
4. aws kms encrypt --key-id alias/keyname --plaintext password --output text
5. put this value into creds.json
