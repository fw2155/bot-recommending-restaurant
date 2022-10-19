import json
import datetime
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
import csv
from io import BytesIO
#https://stackoverflow.com/questions/40741282/cannot-use-requests-module-on-aws-lambda
def lambda_handler(event,context):
    host = 'search-dining-bot-p5bdc3enmnewmrqosj57gshhvm.us-east-1.es.amazonaws.com' 

    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth=('Serendipity59', 'Wfy970509!'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    with open('results.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    count=0
    for restaurant in data:
        index_data = {
            'id': restaurant[0],
            'categories': restaurant[2]
        }
        print ('dataObject', index_data)
        count+=1
        es.index(index="restaurants", doc_type="Restaurant", id=count, body=index_data, refresh=True)