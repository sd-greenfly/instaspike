This script is heavily cribbed from PyInstaStories -- some options have been removed, and boto3 AWS S3 integration has been added.

Steps I took to make it function on my MBP.



1. Install Python 3.7.3
2. use pip3 to install https://github.com/ping/instagram_private_api
3. run  /Applications/Python\ 3.7/Install\ Certificates.command
-- now program can successfully complete login.
4. install awscli using pip3
5. configure awscli -- used my personal s3 account on region: us-west-2
6. make file containing instagram account names one per line -- I tested with nba, nfl, stephenasmith
7. "python3 pycollectstories.py -b usernames -u <my_insta_account> -p <my_insta_pass>"
8. future runs can just be "python3 pycollectstories.py -b usernames"