# yomamabot/fb_yomamabot/urls.py

from django.conf.urls import include, url
from .views import BotView
import bot.views as bot_view

urlpatterns = [
    url(r'^initiate_chat/?$', bot_view.initiate_chat),
    url(r'^6387b4011cfdbb2574595e92200266a344939d861d455c5d08/?$', BotView.as_view())

]
