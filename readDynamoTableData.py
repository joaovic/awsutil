import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('consumer_account_map')

i = 1000000000010

response = table.query(
    KeyConditionExpression=Key('consumer_id').eq(str(i).zfill(19))
)

items = response['Items']
print(items)
