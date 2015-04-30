#-*- coding: utf-8 -*-

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[0:2] < (1, 4):
    from django.conf.urls.defaults import include, patterns, url
else:
    from django.conf.urls import include, patterns, url

from django.views import generic

from django_comments_xtd import views, models, django_comments_urls
from django_comments_xtd.conf import settings


urlpatterns = patterns('',
    url(r'', include(django_comments_urls)),
    url(r'^sent/$', views.sent, name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm, name='comments-xtd-confirm'),
    url(r'^mute/(?P<key>[^/]+)$', views.mute, name='comments-xtd-mute'),
)

if settings.COMMENTS_XTD_MAX_THREAD_LEVEL > 0:
    urlpatterns += patterns("",
        url(r'^reply/(?P<cid>[\d]+)$',   views.reply,   name='comments-xtd-reply'),
    )
