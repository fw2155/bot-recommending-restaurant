import boto3
import json

def lambda_handler(event,context):
    client = boto3.client('dynamodb', region_name='us-east-1')
    
    try:
        resp = client.create_table(
            TableName="yelp-dining",
            #Primary Key
            KeySchema=[
                {
                    "AttributeName": "businessId",
                    "KeyType": "HASH"
                }
            ],
            # Any attributes used in KeySchema or Indexes must be declared in AttributeDefinitions
            AttributeDefinitions=[
                {
                    "AttributeName": "businessId",
                    "AttributeType": "S"
                }
            ],
            # ProvisionedThroughput controls the amount of data you can read or write to DynamoDB per second.
            # You can control read and write capacity independently.
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )
        print("Table created successfully!")
    except Exception as e:
        print("Error creating table:")
        print(e)
        
    return {
        'statusCode':200,
        'body':json.dumps('Hello from lambda')
    }