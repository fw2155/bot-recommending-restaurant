import math
import dateutil.parser
import datetime
import time
import os
import re
import logging
import boto3
import json
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """
def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }
def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
""" --- Helper Functions --- """
def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_order_cuisine(city,cuisine, date, dining_time, number, email):
    cuisine_type = ['mexican', 'chinese', 'japanese','korean','indian']
    support_city={'lynnfield', 'duvall', 'woodside', 'bridgewater', 'larchmont', 'braintree', 'tukwila', 'ridgefield park', 'auburn', 'garden city south', 'silverdale', 'south easton', 'rockland', 'mill valley', 'foxborough', 'danvers', 'ridgefield', 'eastchester', 'jackson heights', 'mukilteo', 'norwell', 'river vale', 'salem', 'lexington', 'sea bright', 'bainbridge island', 'stoughton', 'hoboken', 'wyckoff', 'dracut', 'mineola', 'park ridge', 'brisbane', 'westford', 'sammamish', 'east bridgewater', 'long branch', 'cambridge', 'lincoln park', 'medway', 'greenvale', 'rahway', 'san lorenzo', 'brighton', 'passaic', 'haworth', 'queens', 'jackson heights ', 'south amboy', 'poulsbo', 'concord', 'lynn', 'marshfield', 'newtonville', 'waltham', 'kent', 'tarrytown', 'peabody', 'saugus', 'secaucus', 'richmond hill', 'hercules', 'fort lee', 'elizabeth', 'holliston', 'port chester', 'englewood', 'woodinville', 'pequannock', 'des moines', 'ridgewood', 'hasbrouck heights', 'newcastle', 'sharon', 'wayne', 'forest hills', 'kenmore', 'corona', 'maplewood', 'tenafly', 'garfield', 'san pablo', 'lyndhurst', 'berkeley', 'scituate', 'west roxbury', 'sunnyside', 'glen rock', 'maple valley', 'garwood', 'lynbrook', 'parsippany-troy hills', 'east rockaway', 'white plains', 'kearny', 'andover', 'hillsdale', 'arlington', 'palo alto', 'jamaica plain', 'acton', 'brockton', 'rockaway beach', 'valley stream', 'east orange', 'orange', 'garden city park', 'union', 'ipswich', 'benicia', 'riverdale', 'middleton', 'stewart manor', 'tacoma', 'mountlake terrace', 'revere', 'richmond', 'black diamond', 'howard beach', 'north andover', 'roxbury', 'abng', 'freehold', 'bogota', 'north haledon', 'orinda', 'jamaica', 'renton', 'lawrence', 'woodhaven', 'middletown township', 'bronx', 'edgewater', 'cliffside park', 'sausalito', 'bath beach', 'west hempstead', 'morganville', 'hingham', 'newark', 'redwood city', 'bloomfield', 'elmont', 'south san francisco', 'emeryville', 'snohomish', 'west caldwell', 'pleasant hill', 'marblehead', 'greenpoint', 'mercer island', 'mattapan', 'pinole', 'northvale', 'burlington', 'chelsea', 'fresh meadow', 'whitestone', 'old bridge', 'colonia', 'boston', 'fremont', 'sunset park', 'avenel', 'prospect park', 'cliffwood', 'whitman', 'west new york', 'rockville centre', 'union city', 'franklin', 'hastings on hudson', 'north reading', 'new milford', 'hayward', 'roselle', 'jersey city', 'woodland park', 'hull', 'mamaroneck', 'north arlington', 'brooklyn', 'pine brook', 'pearl river', 'abington', 'monroe', 'swampscott', 'south orange', 'woodbridge township', 'dorchester center', 'island park', 'dobbs ferry', 'flushing', 'pembroke', 'wayland', 'belleville', 'moraga', 'newton', 'edison', 'lynnwood', 'wallington', 'wakefield', 'highlands', 'roslindale', 'springfield', 'paterson', 'foxboro', 'rutherford', 'perth amboy', 'irvington', 'manhattan', 'fairview', 'midland park', 'issaquah', 'san anselmo', 'closter', 'leonia', 'san francisco', 'maspeth', 'fair lawn', 'wood-ridge', 'east elmhurst', 'iselin', 'montvale', 'west orange', 'hewlett', 'fords', 'new hyde park', 'milton', 'paramus', 'kingston', 'sacramento', 'teaneck', 'glen cove', 'hackensack', 'hazlet', 'fairfield', 'floral park', 'weymouth', 'mill creek', 'martinez', 'bayonne', 'winthrop', 'greenwich', 'chelmsford', 'north bergen', 'millbrae', 'elmhurst', 'menlo park', 'san leandro', 'middle village', 'natick', 'beverly', 'half moon bay', 'pelham', 'port orchard', 'moonachie', 'bellevue', 'randolph', 'franklin lakes', 'yonkers', 'allendale', 'dorchester', 'san bruno', 'harrison', 'bremerton', 'stanford', 'shoreline', 'kensington', 'clinton', 'millis', 'rockaway park', 'matawan', 'somerville', 'bedford', 'guttenberg', 'weston', 'malden', 'vallejo', 'orangeburg', 'melrose', 'needham', 'park slope', 'red bank', 'belvedere tiburon', 'river edge', 'maywood', 'framingham', 'little ferry', 'san carlos', 'nutley', 'seattle', 'cresskill', 'keyport', 'norwood', 'oradell', 'livingston', 'hawthorne', 'kirkland', 'the bronx', 'methuen', 'tyngsboro', 'westwood', 'tewksbury', 'san francisco bay area', 'redmond', 'everett', 'astoria', 'albertson', 'glendale', 'foster city', 'manhasset', 'millburn', 'sudbury', 'el cerrito', 'marlboro', 'rye', 'east rutherford', 'pequannock township', 'parsippany', 'waldwick', 'haskell', 'mount vernon', 'bayside', 'chestnut hill', 'brookline', 'pompton plains', 'hastings-on-hudson', 'purchase', 'crown heights', 'scarsdale', 'roselle park', 'staten island', 'burien', 'oakland', 'eatontown', 'medfield', 'el sobrante', 'hillside', 'rego park', 'marlboro township', 'montclair', 'west bridgewater', 'daly city', 'union township', 'verona', 'franklin square', 'piermont', 'ozone park', 'englewood cliffs', 'south richmond hill', 'cranford', 'lafayette', 'redwood shores', 'walpole', 'albany', 'north billerica', 'college point', 'woodbridge', 'ramsey', 'belmont','englishtown', 'kew gardens', 'lowell', 'long beach', 'stoneham', 'garden city', 'wilmington', 'novato', 'lake stevens', 'bergenfield', 'caldwell', 'roxbury crossing', 'elmwood park', 'burlingame', 'larkspur', 'san rafael', 'belford', 'great neck', 'bronxville', 'south hackensack', 'tappan', 'queens village', 'long island city', 'south ozone park', 'canton', 'clifton', 'wellesley', 'fresh meadows', 'lodi', 'east bronx', 'palisades park', 'holbrook', 'long island city ', 'covington', 'dedham', 'hanover', 'new york', 'lake forest park', 'mansfield', 'pacifica', 'hartsdale', 'pompton lakes', 'kenilworth', 'douglaston', 'middletown', 'rochelle park', 'new rochelle', 'oceanside', 'dumont', 'rodeo', 'halifax', 'reading', 'port washington', 'seatac', 'baldwin', 'medford', 'walnut creek', 'edmonds', 'westfield', 'woburn', 'little neck', 'atlantic highlands', 'watertown', 'winchester', 'alameda', 'castro valley', 'billerica', 'glen oaks', 'north chelmsford', 'roslyn', 'cohasset', 'allston', 'hyde park', 'mountain view', 'wyk', 'westbury', 'bothell', 'easton', 'gig harbor', 'plainville', 'little falls', 'san mateo', 'oakland gardens', 'federal way', 'colma', 'williston park', 'quincy', 'north quincy', 'linden'}
    if city is not None:
        if city.lower() not in support_city:
            return build_validation_result(False,
                                           'Location',
                                           'Sorry.We do not support {} now.'
                                           'We currently support cities in New York State, San Fransico, Seattle and Boston'.format(city))
    if cuisine is not None and cuisine.lower() not in cuisine_type:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not have {}, would you choose a different type of cuisine?  '
                                       'Our most popular cuisine are Chinese, Japanese, Korean, Indian, Mexican'.format(cuisine))
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'DiningDate', 'I did not understand that, what date would you like to dine in?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'You can dine in from tomorrow onwards. What day would you like to dine in?')
    if dining_time is not None:
        if len(dining_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)
        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)
        if hour < 9 or hour > 23:
            # Outside of business hours
            return build_validation_result(False, 'DiningTime', 'Most restaurants open from 9 a m. to 23 p m. Can you specify a time during this range?')
    if number is not None:
        num = parse_int(number)
        if num <= 0 or num >= 50:
            return build_validation_result(False,'NumOfPeople', 'Please input a number between 1~50. Most restaurants serve at most 50 people in a group.')
    if email is not None:
        EMAIL_REGEX = re.compile(r"""(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#'$"""+
    r"""%&*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d"""+
    r"""-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*"""+
    r"""[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4]["""+
    r"""0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|["""+
    r"""a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|"""+
    r"""\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
        if not re.match(EMAIL_REGEX,email):
            return build_validation_result(False, 'Email', 'Please enter a valid email.')
    return build_validation_result(True, None, None)

#push records to SQS
def pushRecord(event):
    SQS = boto3.client('sqs')
    records=event.get('data')
    logger.debug('in function')
    try:
        response=SQS.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/698543564037/DiningBotQueue',
            MessageBody="Dining bot records user input",
            MessageAttributes={
                "Location": {
                    "StringValue": str(get_slots(event)["Location"]),
                    "DataType": "String"
                },
                "Cuisine": {
                    "StringValue": str(get_slots(event)["Cuisine"]),
                    "DataType": "String"
                },
                "DiningDate" : {
                    "StringValue": get_slots(event)["DiningDate"],
                    "DataType": "String"
                },
                "DiningTime" : {
                    "StringValue": str(get_slots(event)["DiningTime"]),
                    "DataType": "String"
                },
                "NumOfPeople" : {
                    "StringValue": str(get_slots(event)["NumOfPeople"]),
                    "DataType": "String"
                },
                "Email" : {
                    "StringValue": str(get_slots(event)["Email"]),
                    "DataType": "String"
                }
            }
        )
        logger.debug('success')
    except Exception as e:
        logger.debug('bug')
        raise Exception("Fail to record %s" % e)


""" --- Functions that control the bot's behavior --- """
def recommend_cuisine(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    city=get_slots(intent_request)["Location"]
    cuisine_type = get_slots(intent_request)["Cuisine"]
    date = get_slots(intent_request)["DiningDate"]
    dine_time = get_slots(intent_request)["DiningTime"]
    number = get_slots(intent_request)["NumOfPeople"]
    email = get_slots(intent_request)["Email"]
    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)
        validation_result = validate_order_cuisine(city,cuisine_type, date, dine_time, number,email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        # if number is not None:
        #     output_session_attributes['Price'] = int(number) * 5  # Elegant pricing model
        return delegate(output_session_attributes, get_slots(intent_request))
     
    
    #snsmessage = {'content': 'Okay, your interest in {} cuisine in {} on {} at {} has been recorded. And there will be {} in your group. I will send a text message to your phone {} once we found suitable recommendations'.format(cuisine_type, city, date, dine_time, number,phonenumber)}
    #snsmessage = {"test":"message test"}
    # sns.publish(
    #     #TopicArn='YOUR_Topic_ARN', 
    #     Message=json.dumps(snsmessage)
    # )
    
    pushRecord(intent_request)
    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Got it. I will send an email to {} once I found the list of restaurant suggestions.'.format(email)})
""" --- Intents --- """
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestIntent':
        return recommend_cuisine(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')
""" --- Main handler --- """
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)