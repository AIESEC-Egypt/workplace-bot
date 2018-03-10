# yomamabot/fb_yomamabot/views.py
import csv
import datetime
import json
import re
from pprint import pprint

import requests
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from bot import constants
from bot.models import BasicAnalytic, AccessToken, CoreUser, DAAL


def post_facebook_message(fbid, message_body, payload=None):
    post_message_url = constants.BASE_URL + '/me/messages?access_token=' + constants.PAGE_ACCESS_TOKEN

    response_msg = json.JSONEncoder().encode(
        {"messaging_type": "RESPONSE", "recipient": {"id": fbid}, "message": message_body})

    # print(response_msg)
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    # pprint(status.json())


# Create your views here.
class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == constants.VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # pprint(incoming_message)
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        if incoming_message['object'] == 'page':
            for entry in incoming_message['entry']:
                for message in entry['messaging']:
                    # Check to make sure the received call is a message call
                    # This might be delivery, optin, postback for other events
                    if 'message' in message:
                        # print(message)
                        self.received_message(message)

                        # assuming obj is your model instance
                        # result = create_snapshot_analytic(1609, '1/8/2017', '1/8/2018')
                        # dict_obj = model_to_dict(result)
                        # serialized = json.dumps(dict_obj)

                        # post_facebook_message(message['sender']['id'], "Test text")
        return HttpResponse()

    def received_message(self, message_event):
        senderID = message_event['sender']['id']
        timeOfMessage = message_event['timestamp']
        message = message_event['message']
        text = message['text']

        core_user, created = CoreUser.objects.get_or_create(pk=senderID)
        if created:
            core_user.name = get_name(senderID)
            core_user.save()
            print(core_user)

        if core_user.initiated_conversation and core_user.path is None:
            if message['quick_reply']['payload'] == 'DAAL':
                core_user.path = 'DAAL'
                process_daal_path(core_user, text)
            if message['quick_reply']['payload'] == 'Analytics':
                core_user.path = 'Analytics'
                process_analytics_path(core_user, text)
            core_user.save()
        elif core_user.path == 'Analytics':
            process_analytics_path(core_user, text)
        elif core_user.path == 'DAAL':
            process_daal_path(core_user, message)
        else:
            if findWholeWord('Hi')(text) is not None:
                # Initiate a Conversation Here with the User
                initiate_conversation(core_user)
            else:
                message_body = {
                    "text": "Please start the conversation with me with typing Hi"
                }
                post_facebook_message(core_user.id, message_body)

        print('Received message from user {0} at {1} with message:{2}'.format(senderID, timeOfMessage, message))


def process_daal_path(core_user, message):
    text = message['text']
    if core_user.third_question_daal:
        send_thank_you_daal(core_user, text)
    elif core_user.second_question_daal:
        process_question_three_daal(core_user, text)
    elif core_user.first_question_daal:
        process_question_two_daal(core_user, message)
    elif core_user.initiated_conversation:
        ask_question_one_daal(core_user)


def ask_question_one_daal(core_user):
    message_body = {
        "text": "Which program would you like to approve in?",
        "quick_replies": [
            {
                "content_type": "text",
                "title": "IGV",
                "payload": "IGV"
            },
            {
                "content_type": "text",
                "title": "IGE",
                "payload": "IGE"
            },
            {
                "content_type": "text",
                "title": "IGT",
                "payload": "IGT"
            },
            {
                "content_type": "text",
                "title": "OGV",
                "payload": "OGV"
            },
            {
                "content_type": "text",
                "title": "OGE",
                "payload": "OGE"
            },
            {
                "content_type": "text",
                "title": "OGT",
                "payload": "OGT"
            }
        ]
    }
    post_facebook_message(core_user.id, message_body)
    core_user.first_question_daal = True
    core_user.save()


def process_question_two_daal(core_user, message):
    core_user.daal = DAAL()
    core_user.daal.product = message['quick_reply']['payload']
    core_user.daal.save()
    core_user.second_question_daal = True
    core_user.save()
    message_body = {
        "text": "Great, Now that I know that you would like to approve in " + core_user.daal.product + " ,I will get you the rankings of who approve the most? But first give me a start date\nEnter the date in format \'dd/mm/yy\'"
    }
    post_facebook_message(core_user.id, message_body)


def process_question_three_daal(core_user, text):
    if ValidateDate(text):
        message_body = {
            "text": "Great, Now that I have the start date, Can you please provide me with the end date for your analytics?\nEnter the date in format \'dd/mm/yy\'"
        }
        core_user.daal.start_date = ValidateDate(text, True)
        core_user.daak.save()
        core_user.third_question_daal = True
        core_user.save()
    else:
        message_body = {
            "text": "I'm sorry, I won't be able to proceed unless I have the end date.\nPlease enter the date in format \'dd/mm/yy\'."
        }
    post_facebook_message(core_user.id, message_body)


def send_thank_you_daal(core_user, text):
    if ValidateDate(text):
        message_body = {
            "text": "Thank you for reaching out to me, I'm currently extracting your desired data. \nGive me a second."
        }

        core_user.daal.end_date = ValidateDate(text, True)
        core_user.daal.save()
        core_user.daal.process_daal()
        message_body = {
            "text": "Thank you for reaching out to me, I'm currently extracting your desired data. \nGive me a second."
        }

        post_facebook_message(core_user.id, message_body)
        core_user.restart_process_daal()
    else:
        message_body = {
            "text": "I'm sorry, I won't be able to proceed unless I have the end date for the analytics.\nPlease enter the date in format \'dd/mm/yy\'."
        }
        post_facebook_message(core_user.id, message_body)


def process_analytics_path(core_user, text):
    if core_user.third_question:
        send_thank_you(core_user, text)
    elif core_user.second_question:
        process_question_three(core_user, text)
    elif core_user.first_question:
        process_question_two(core_user, text)
    elif core_user.initiated_conversation:
        ask_question_one(core_user)


def ask_question_one(core_user):
    message_body = {
        "text": "Please provide me with the ID of your Entity.\nExample (AIESEC in Egypt's ID is 1609), so type 1609."
    }
    post_facebook_message(core_user.id, message_body)
    core_user.first_question = True
    core_user.save()


def process_question_two(core_user, text):
    if RepresentsInt(text):
        message_body = {
            "text": "Great, Now that I have your Entity's ID, Can you please provide me with the start date for your analytics?\nEnter the date in format \'dd/mm/yy\'"
        }
        core_user.basic_analytic = BasicAnalytic(id=int(text))
        core_user.basic_analytic.save()
        core_user.second_question = True
        core_user.save()
    else:
        message_body = {
            "text": "I'm sorry, I won't be able to proceed unless I have the ID of the Entity that you would like to get the analytics for.\nPlease just type the number."
        }
    post_facebook_message(core_user.id, message_body)


def process_question_three(core_user, text):
    if ValidateDate(text):
        message_body = {
            "text": "Great, Now that I have the start date, Can you please provide me with the end date for your analytics?\nEnter the date in format \'dd/mm/yy\'"
        }
        core_user.basic_analytic.start_date = ValidateDate(text, True)
        core_user.basic_analytic.save()
        core_user.third_question = True
        core_user.save()
    else:
        message_body = {
            "text": "I'm sorry, I won't be able to proceed unless I have the start date for the analytics.\nPlease enter the date in format \'dd/mm/yy\'."
        }
    post_facebook_message(core_user.id, message_body)


def send_thank_you(core_user, text):
    if ValidateDate(text):
        message_body = {
            "text": "Thank you for reaching out to me, I'm currently extracting your desired data. \nGive me a second."
        }
        post_facebook_message(core_user.id, message_body)
        core_user.basic_analytic.end_date = ValidateDate(text, True)
        core_user.basic_analytic.save()
        result = create_snapshot_analytic(core_user)

        message_body = {
            "text": result.construct_analytics_message()
        }
        post_facebook_message(core_user.id, message_body)
        core_user.restart_process()
    else:
        message_body = {
            "text": "I'm sorry, I won't be able to proceed unless I have the end date for the analytics.\nPlease enter the date in format \'dd/mm/yy\'."
        }
        post_facebook_message(core_user.id, message_body)


def initiate_conversation(core_user):
    message_body = {
        "text": "Hi " + core_user.name + ", I was initiated a couple of days ago. I offer these kind of services, can you please choose one?",
        "quick_replies": [
            {
                "content_type": "text",
                "title": "Analytics",
                "payload": "Analytics"
            },
            {
                "content_type": "text",
                "title": "DAAL - Approvals",
                "payload": "DAAL"
            }
        ]
    }
    post_facebook_message(core_user.id, message_body)
    core_user.initiated_conversation = True
    core_user.save()





def get_name(senderID):
    result = requests.get(constants.BASE_URL + '/' + senderID + '/?access_token=' + constants.PAGE_ACCESS_TOKEN).json()
    name = result['name']
    return name


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def RepresentsInt(s):
    return re.match(r"[-+]?\d+$", s) is not None


def ValidateDate(d, extract=False):
    if not extract:
        isValidDate = True
        try:
            day, month, year = d.split('/')
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            isValidDate = False

        return isValidDate
    else:
        day, month, year = d.split('/')
        return datetime.datetime(int(year), int(month), int(day))


def create_snapshot_analytic(core_user):
    # Analytics
    OPPORTUNITY_TYPE = ['opportunity', 'person']
    PROGRAM_ID = [1, 2, 5]

    # Request iGV Analytics
    office_id = core_user.basic_analytic.id
    start_date = str(core_user.basic_analytic.start_date)
    end_date = str(core_user.basic_analytic.end_date)
    result = analytics_request(OPPORTUNITY_TYPE[0], office_id, PROGRAM_ID[0], start_date,
                               end_date)

    pprint('Started parsing the analytics for you.')
    if 'analytics' in result:
        analytics = core_user.basic_analytic
        analytics.igv_applications = result['analytics']['total_applications']['doc_count']
        analytics.igv_approved = result['analytics']['total_approvals']['doc_count']
        analytics.igv_realized = result['analytics']['total_realized']['doc_count']
        analytics.igv_finished = result['analytics']['total_finished']['doc_count']
        analytics.igv_completed = result['analytics']['total_completed']['doc_count']

    # Request iGT Analytics
    result = analytics_request(OPPORTUNITY_TYPE[0], office_id, PROGRAM_ID[1], start_date,
                               end_date)
    if 'analytics' in result:
        analytics.igt_applications = result['analytics']['total_applications']['doc_count']
        analytics.igt_approved = result['analytics']['total_approvals']['doc_count']
        analytics.igt_realized = result['analytics']['total_realized']['doc_count']
        analytics.igt_finished = result['analytics']['total_finished']['doc_count']
        analytics.igt_completed = result['analytics']['total_completed']['doc_count']

    # Request iGE Analytics
    result = analytics_request(OPPORTUNITY_TYPE[0], office_id, PROGRAM_ID[2], start_date,
                               end_date)
    if 'analytics' in result:
        analytics.ige_applications = result['analytics']['total_applications']['doc_count']
        analytics.ige_approved = result['analytics']['total_approvals']['doc_count']
        analytics.ige_realized = result['analytics']['total_realized']['doc_count']
        analytics.ige_finished = result['analytics']['total_finished']['doc_count']
        analytics.ige_completed = result['analytics']['total_completed']['doc_count']

    # Request oGV Analytics
    result = analytics_request(OPPORTUNITY_TYPE[1], office_id, PROGRAM_ID[0], start_date,
                               end_date)
    if 'analytics' in result:
        analytics.ogv_applications = result['analytics']['total_applications']['doc_count']
        analytics.ogv_approved = result['analytics']['total_approvals']['doc_count']
        analytics.ogv_realized = result['analytics']['total_realized']['doc_count']
        analytics.ogv_finished = result['analytics']['total_finished']['doc_count']
        analytics.ogv_completed = result['analytics']['total_completed']['doc_count']

    # Request oGT Analytics
    result = analytics_request(OPPORTUNITY_TYPE[1], office_id, PROGRAM_ID[1], start_date,
                               end_date)
    if 'analytics' in result:
        analytics.ogt_applications = result['analytics']['total_applications']['doc_count']
        analytics.ogt_approved = result['analytics']['total_approvals']['doc_count']
        analytics.ogt_realized = result['analytics']['total_realized']['doc_count']
        analytics.ogt_finished = result['analytics']['total_finished']['doc_count']
        analytics.ogt_completed = result['analytics']['total_completed']['doc_count']
    # Request oGE Analytics
    result = analytics_request(OPPORTUNITY_TYPE[1], office_id, PROGRAM_ID[2], start_date,
                               end_date)
    if 'analytics' in result:
        analytics.oge_applications = result['analytics']['total_applications']['doc_count']
        analytics.oge_approved = result['analytics']['total_approvals']['doc_count']
        analytics.oge_realized = result['analytics']['total_realized']['doc_count']
        analytics.oge_finished = result['analytics']['total_finished']['doc_count']
        analytics.oge_completed = result['analytics']['total_completed']['doc_count']

    analytics.total_applications = analytics.ige_applications + analytics.igt_applications + analytics.igv_applications + analytics.oge_applications + analytics.ogt_applications + analytics.ogv_applications
    analytics.total_approved = analytics.ige_approved + analytics.igt_approved + analytics.igv_approved + analytics.oge_approved + analytics.ogt_approved + analytics.ogv_approved
    analytics.total_realized = analytics.ige_realized + analytics.igt_realized + analytics.igv_realized + analytics.oge_realized + analytics.ogt_realized + analytics.ogv_realized
    analytics.total_finished = analytics.ige_finished + analytics.igt_finished + analytics.igv_finished + analytics.oge_finished + analytics.ogt_finished + analytics.ogv_finished
    analytics.total_completed = analytics.ige_completed + analytics.igt_completed + analytics.igv_completed + analytics.oge_completed + analytics.ogt_completed + analytics.ogv_completed

    return analytics


def analytics_request(type, office_id, program_id, start_date, end_date):
    access_token, created = AccessToken.objects.get_or_create(id=1)
    if created:
        access_token.save()
    url = 'https://gis-api.aiesec.org/v2/applications/analyze?access_token=' + access_token.value + '&basic[type]=' + type + '&basic[home_office_id]=' + str(
        office_id) + '&programmes%5B%5D=' + str(
        program_id) + '&start_date=' + start_date + '&end_date=' + end_date
    r = requests.get(url).json()
    return r
