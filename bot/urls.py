# yomamabot/fb_yomamabot/urls.py

from django.conf.urls import include, url
from .views import BotView

urlpatterns = [
    url(r'^(?P<uuid>[0-9A-Za-z]+)/?$', BotView.as_view()),
    url(r'^6387b4011cfdbb2574595e92200266a344939d861d455c5d08/?$', BotView.as_view())
]
