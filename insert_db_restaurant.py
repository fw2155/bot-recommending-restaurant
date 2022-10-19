import boto3
from botocore.exceptions import ClientError
import requests
import json
from decimal import Decimal
import datetime

def lambda_handler(event,context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-dining')
    
    # Define the API key, Define the endpoint, and define the header
    API_KEY = 'zo6VF1DQXgmoqoGYPpxYWa-o96ACWzk30DT1Jmv0SBv1rHKsHMuqwIXl6u2kF67oQfDCPKeTBHnD2q1ic1VSfV57kl0xevT1rSkcplQ2lRwqKSwMq9dUYTxKy1NLY3Yx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}
    #'chinese','japanese','korean','indian','mexican'
    cuisine_types = ['chinese','japanese','korean','indian','mexican'] 
    
    for cuisine_type in cuisine_types:
        offset = 0
        for i in range(0, 20):
            offset += 50
            PARAMETERS = {
                'term': 'restaurant',
                'location': 'Boston',
                'radius': 40000,
                'categories': cuisine_type,
                'limit': 50,
                'offset': offset,
                'sort_by': 'rating'
            }
            #import urllib3
            #http = urllib3.PoolManager()
            #r = http.request('GET', 'http://httpbin.org/robots.txt')
            response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
            business_data = response.json()
            print(business_data)
            for each in business_data['businesses']:
                try:
                    #print(each['id'], each['name'],each['categories'][0]['alias'],each['location']['city'])
                    table.put_item(
                        Item={
                            'businessId': each['id'],
                            'name': each['name'],
                            'category': each['categories'][0]['alias'],
                            'address': each['location']['address1'],
                            'city': each['location']['city'],
                            'zipcode': each['location']['zip_code'],
                            'latitude': Decimal(str(each['coordinates']['latitude'])),
                            'longitude': Decimal(str(each['coordinates']['longitude'])),
                            'reviewCount': each['review_count'],
                            'rating': Decimal(str(each['rating'])),
                            'insertedAtTimestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        },
                        ConditionExpression='attribute_not_exists(businessId) AND attribute_not_exists(insertedAtTimestamp)'
                    )
                except ClientError as e:
                    print(e.response['Error']['Code'])