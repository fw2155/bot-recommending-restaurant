# Assignment 1 bot-recommending-restaurant
link: http://hw1-fw2155.s3-website-us-east-1.amazonaws.com/

## AWS
1. S3 (store front-end)
2. API gateway & IAM 
3. Lambda (write functions)
4. Amazon Lex (the bot)
5. Amazon Open Search Service (Elastic Search on businessId and cuisine)
6. Cloud shell (check elastic search search request)
7. Cloud Watch (debug Ծ‸Ծ and set 1 minute trigger on LF2 to check queue)
8. Dynamodb (store 5271 data)
9. Amazon Simple Email Service (send email)
10. Simple Queue Service (store collected client info, lambda(LF1)->queue->ses)

## Record info
First, clients can talk with bot to specify preference.
Validation:
1. check city (must in New York/San Fransico/Seattle/Boston)
2. check cuisine (must be chinese/korean/japanese/mexican/indian)
3. check date (must from tomorrow onwards)
4. check time (must between 9am-23pm)
5. check number of people (must between 1~50)
6. check email (must be a valid email)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/1.png)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/2.png)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/3.png)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/4.png)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/5.png)

## Prepare SQS and sent email
### SQS records
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/queue1.png)
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/queue2.png)
### if found, sent a success email to client
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/result.png)
### if not found, sent a failure email to client
![alt text](https://github.com/fw2155/bot-recommending-restaurant/blob/main/screenshot/notfound4.png)

