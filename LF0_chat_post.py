import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    print ("here",json.dumps(event))
    event_body = json.loads(event['body'])
    message=event_body['messages'][0]['unstructured']['text']
    print(message)
    client = boto3.client('lex-runtime', region_name = 'us-east-1')
    response = client.post_text(
      botName='DiningBot',
      botAlias='DiningBot',
      userId='string',
      inputText=message,
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({"messages":
            [{
                "type": "unstructured",
                "unstructured": {
                "id":'string',
                "text":response['message'],
                #"timestamp": getTimeStamp
            }
            }]
            
        })
    }
