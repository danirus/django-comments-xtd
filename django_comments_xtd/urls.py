from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views import generic

from django_comments_xtd import views, models


urlpatterns = patterns('',
    url(r'', include("django.contrib.comments.urls")),

    url(r'sent/$',                   views.sent,    name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm, name='comments-xtd-confirm'),
)
