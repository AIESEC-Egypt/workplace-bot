# yomamabot/fb_yomamabot/urls.py

from django.conf.urls import include, url
from .views import YoMamaBotView

urlpatterns = [
    url(r'^6387b4011cfdbb2574595e92200266a344939d861d455c5d08/?$', YoMamaBotView.as_view())
]
