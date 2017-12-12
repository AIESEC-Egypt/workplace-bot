# yomamabot/fb_yomamabot/views.py
import json
import requests
from pprint import pprint

from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "DQVJ0RTBva0ZAzUzBzTUVFcU1TRWlRSy1GZAEV3cWRkQUxLNkNNaFF6bGYyanRzMUxfR3FuUVJoNlFuelo5bjQxTkdsMG0wRTR2cE40LXpDRDZAnakFQS3h4TVJuREc5TFdGcUZATVGVLTkFldEZADZAUhILXZAjOFQzbmtxZA3drUDc3a2lFa0x1WUF3OVhEaFU1ZAzEyWFNBUDA0Xzdyb3hmcUl4aWhIRWxnQWxkYzZAadmdpTFVMc1ZAYWHZAYdkc3SWJ0T3dvSXVrZAzdn"
VERIFY_TOKEN = "2318934571"


def post_facebook_message(fbid, received_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + PAGE_ACCESS_TOKEN
    response_msg = json.dumps(
        {"messaging_type": "RESPONSE", "recipient": {"id": fbid}, "message": {"text": received_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


# Create your views here.
class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
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
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
