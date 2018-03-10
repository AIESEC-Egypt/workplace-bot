import requests
from django.conf import settings
from django_cron import CronJobBase, Schedule

from bot import constants, create_token
from bot.models import Member, AccessToken
from bot.views import post_facebook_message


class UpdateAccessToken(CronJobBase):
    RUN_EVERY_MINS = 1 if settings.DEBUG else 60  # 6 hours when not DEBUG

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.UpdateAccessToken'

    def do(self):
        self.create_token()

    def create_token(self):
        gis = create_token.GIS()
        access_token, created = AccessToken.objects.get_or_create(id=1)
        access_token.value = gis.generate_token('ali.soliman95@gmail.com', 'thebest1')
        access_token.save()


class InitiateCheckin(CronJobBase):
    RUN_EVERY_MINS = 1 if settings.DEBUG else 10  # 6 hours when not DEBUG

    # Additional Settings
    # RUN_AT_TIMES = ['11:30', '14:00', '23:15']
    ALLOW_PARALLEL_RUNS = True

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'bot.Initiate'

    def do(self):
        update_members()


def update_members():
    members = group_members()
    contact_group(members)


def group_members():
    members_url = "https://graph.facebook.com/%s/members?access_token=%s" % (
    constants.GROUP_ID, constants.PAGE_ACCESS_TOKEN)
    response = requests.get(members_url)
    return response.json()['data']  # List of members {id, name}


def contact_group(group):
    members = []
    members_data = group_members()

    for member in members_data:
        try:
            exists = Member.objects.get(pk=member['id'])
            members.append(exists)
        except:
            new_member = Member(pk=member['id'], name=member['name'], status=2)
            new_member.save()
            members.append(new_member)


def initiate_conversation(member):
    welcome_message = [
        'Howdy %s, I hope that you\'re having a fruitful day today'
    ]

    post_facebook_message(member.id, welcome_message[0])
