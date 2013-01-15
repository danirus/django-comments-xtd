from django.conf.urls.defaults import patterns, include, url
from django.views import generic

from django_comments_xtd import views, models
from django_comments_xtd.conf import settings


urlpatterns = patterns('',
    url(r'', include("django.contrib.comments.urls")),
    url(r'^sent/$',                  views.sent,    name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm, name='comments-xtd-confirm'),
)

if settings.COMMENTS_XTD_MAX_THREAD_LEVEL > 0:
    urlpatterns += patterns("",
        url(r'^reply/(?P<cid>[\d]+)$',   views.reply,   name='comments-xtd-reply'),
    )
