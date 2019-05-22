import boto3


def get_all_usernames():
    table = dynamodb_resource.Table(profile_table_name)
    response = table.scan(
        FilterExpression=Attr("ScanUntil").gt(int(time.time()))
    )
    return response['Items']


def get_number_shards(list_size, shard_size):
    if list_size == 0:
        print("no users to scan currently")
        num_shards = 0
        exit(0)
    elif list_size <= shard_size:
        print("one shard only")
        num_shards = 1
    else:
        num_shards = list_size//shard_size
        if list_size%shard_size > 0:
            num_shards += 1
    return num_shards


def handler(event, context):
    # get list of accounts to scan from profile table
    users_to_check = []
    shard_size = 2
    for item in get_all_usernames():
        users_to_check.append(item['ProfileName'])
    # first pass, just send the list of all usernames to SNS queue
        
#    total_shards = get_number_shards(len(users_to_check), shard_size)
#    for x in range(total_shards):
#        shard_users = users_to_check[x*shard_size:((x+1)*shard_size)+1]

    # include name of ig account to use creds for
    # send those pieces into event to trigger FeedBearBot
