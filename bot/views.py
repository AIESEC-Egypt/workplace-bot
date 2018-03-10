# yomamabot/fb_yomamabot/views.py
import json
from pprint import pprint

import requests
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from bot import constants
from bot.models import BasicAnalytic, AccessToken


def post_facebook_message(fbid, received_message, payload=None):
    post_message_url = 'https://graph.facebook.com/v2.11/me/messages?access_token=' + constants.PAGE_ACCESS_TOKEN

    response_msg = json.JSONEncoder().encode(
        {"messaging_type": "RESPONSE", "recipient": {"id": fbid}, "message": {
            "text": "Hi Ali, your opinion matters to us. Do you have a few seconds to answer a quick survey?",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Yes",
                    "payload": "START_SURVEY"
                },
                {
                    "content_type": "text",
                    "title": "Not now",
                    "payload": "DELAY_SURVEY"
                }
            ]
        }})

    print(response_msg)
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
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
                        # Print the message to the terminal
                        # pprint(message)

                        # assuming obj is your model instance
                        # result = create_snapshot_analytic(1609, '1/8/2017', '1/8/2018')
                        # dict_obj = model_to_dict(result)
                        # serialized = json.dumps(dict_obj)

                        # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                        # are sent as attachments and must be handled accordingly.
                        post_facebook_message(message['sender']['id'], "Test text")
        return HttpResponse()

    def received_message(self, message_event):
        senderID = message_event['sender']['id'];
        recipientID = message_event['recipient']['id'];
        timeOfMessage = message_event['timestamp']
        message = message_event['message']

        print('Received message from user {0} and page {1} at {2} with message:{3}'.format(senderID, recipientID,
                                                                                           timeOfMessage, message))

        messageID = message['mid']

        try:
            isEcho = message['is_echo']
            appID = message['app_id']
            metadata = message['metadata']
            quickReply = message['quick_reply']
        except:
            pass


def create_snapshot_analytic(office_id, start_date, end_date):
    # Analytics
    OPPORTUNITY_TYPE = ['opportunity', 'person']
    PROGRAM_ID = [1, 2, 5]

    # Request iGV Analytics
    result = analytics_request(OPPORTUNITY_TYPE[0], office_id, PROGRAM_ID[0], start_date,
                               end_date)

    pprint('Started parsing the analytics for you.')
    if 'analytics' in result:
        analytics = BasicAnalytic()
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
