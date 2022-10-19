import boto3
import json
import logging
import random
import urllib3
#from boto3.dynamodb.conditions import Key, Attr
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def receiveInfoFromSQS():
    sqs = boto3.client("sqs")
    response = sqs.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/698543564037/DiningBotQueue', 
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    try:
        record = response['Messages'][0]
        if record is None:
            print("Empty message")
            return None
    except KeyError:
        print("No message in the queue")
        return None
    record = response['Messages'][0]
    sqs.delete_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/698543564037/DiningBotQueue',
            ReceiptHandle=record['ReceiptHandle']
        )
    return record

def lambda_handler(event, context):
    #get info from SQS and store it and check database and elastic search
    record = receiveInfoFromSQS() #data will be a json object
    if record is None:
        print("No record in SQS")
        return
    cuisine = record["MessageAttributes"]["Cuisine"]["StringValue"]
    location = record["MessageAttributes"]["Location"]["StringValue"]
    date = record["MessageAttributes"]["DiningDate"]["StringValue"]
    time = record["MessageAttributes"]["DiningTime"]["StringValue"]
    number = record["MessageAttributes"]["NumOfPeople"]["StringValue"]
    email = record["MessageAttributes"]["Email"]["StringValue"]
    print(cuisine)
    #send elastic search query, find matched cuisine
    searchES = 'https://search-dining-bot-p5bdc3enmnewmrqosj57gshhvm.us-east-1.es.amazonaws.com/restaurants/Restaurant/_search?q={}'.format(cuisine)
    #print(searchES)
    http = urllib3.PoolManager()
    #response = http.request('GET', searchES)
    print('hi')
    #print(json.loads(response))
    #data = json.loads(response.data)
    responseES = requests.get(searchES, auth=('Serendipity59', 'Wfy970509!'))
    print(responseES.status_code)
    data = json.loads(responseES.content.decode('utf-8'))
    try:
        dataFromES = data["hits"]["hits"]
    except KeyError:
        logger.debug("Error extracting hits from ES response")
    
    # get business ID from Elastic Search
    businessIDs = []
    for restaurant in dataFromES:
        businessIDs.append(restaurant["_source"]["id"])
    
    messageToSend = 'Hey, I find a nice {} restaurant in {} that can serve {} people on {} at {}.'.format(cuisine, location, number, date, time)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-dining')
    print(len(businessIDs))
    fetched_name,fetched_address,fetched_zipcode,fetched_rating,fetched_reviewCount='','','','',''
    #randomIndex=random.randint(0, len(businessIDs)-1)
    #randombusinessID=businessIDs[randomIndex]
    find=False
    for i in range(len(businessIDs)):
        getOne=businessIDs[i]
        response = table.get_item(
            Key={
                'businessId': getOne
            }
        )
        item = response.get("Item")
        fetched_city = item['city']
        if fetched_city.lower()!=location.lower():
            continue
        else:
            fetched_name = item['name']
            #fetched_category = item['category']
            fetched_address = item['address']
            #fetched_city = item['city']
            fetched_zipcode = item['zipcode']
            fetched_rating = str(item['rating'])
            fetched_reviewCount = str(item['reviewCount'])
            find=True
            break
    print(len(businessIDs),find)
    # response = table.scan(FilterExpression=Attr('businessId').eq(randombusinessID))
    # item = response['Items'][0]
    restaurantMsg = 'Restaurant Info:'
    # name = item["name"]
    # address = item["address"]
    if find==True:
        restaurantMsg += '\n'+fetched_name +', located at ' + fetched_address +', '+ fetched_zipcode
        ratingMessage='Rating: '+ fetched_rating
        reviewMessage='Review counts: '+fetched_reviewCount
        messageToSend +='\n'+restaurantMsg+'\n'+ratingMessage+'\n'+reviewMessage+'\n'+"Enjoy your meal:)"
        print(messageToSend)
    # try:
    #     client = boto3.client('ses', region_name= 'ap-southeast-1')
    #     response = client.publish(
    #         Email=email,
    #         Message= messageToSend,
    #         MessageStructure='string'
    #     )
    # except KeyError:
    #     logger.debug("Error sending")
    
    
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    if find==False:
        response = ses_client.send_email(
        Destination={
            "ToAddresses":[email]
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": 'Sorry after searching our database, we cannot find {} cuisine that is in {}. We will improve our database asap!'.format(cuisine,location),
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Sorry we cannot give restaurant suggestion based on your need",
            },
        },
        Source="jilinwfy@gmail.com",
        )
    if find==True:
        response = ses_client.send_email(
            Destination={
                "ToAddresses":[email]
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": CHARSET,
                        "Data": messageToSend,
                    }
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": "Hey, this is your restaurant suggestion!",
                },
            },
            Source="jilinwfy@gmail.com",
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps("Hello from LF2 running smoothly")
    }
    