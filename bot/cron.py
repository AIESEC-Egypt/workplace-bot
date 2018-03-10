import requests
from django.conf import settings
from django_cron import CronJobBase, Schedule

from bot import constants, create_token
from bot.models import AccessToken
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