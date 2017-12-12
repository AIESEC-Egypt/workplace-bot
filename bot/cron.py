import requests
from bot import constants

from django_cron import CronJobBase, Schedule

from django.conf import settings

from bot.models import Member


class InitiateCheckin(CronJobBase):
    RUN_EVERY_MINS = 1 if settings.DEBUG else 10  # 6 hours when not DEBUG

    # Additional Settings
    # RUN_AT_TIMES = ['11:30', '14:00', '23:15']
    ALLOW_PARALLEL_RUNS = True

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'bot.Initiate'

    def do(self):
        initiate_chat()


def initiate_chat():
    members = group_members()
    contact_group(members)


def group_members():
    get_members_url = "https://graph.facebook.com/%s/members?access_token=%s" %(constants.GROUP_ID ,constants.PAGE_ACCESS_TOKEN)
    response = requests.get(get_members_url)
    print(response.json())
    return response.json()['data']  # List of members {id, name}

def contact_group(group):
    for member in group:
        member_id = member['id']
        post_facebook_message(member_id, "Hi %s"%member['name'])


def save_members(request):

    members = group_members()

    for member in members:
        try:
            exists = Member.objects.get(pk=member['id'])
        except:
            new_member = Member(pk=member['id'], name=member['name'], status=2)
            new_member.save()
