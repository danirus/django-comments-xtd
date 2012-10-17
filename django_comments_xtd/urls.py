from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views import generic

from django_comments_xtd import views, models


allow_comment_threads = getattr(settings, "COMMENTS_XTD_MAX_THREAD_LEVEL", 0)


urlpatterns = patterns('',
    url(r'', include("django.contrib.comments.urls")),
    url(r'^sent/$',                  views.sent,    name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm, name='comments-xtd-confirm'),
)

if allow_comment_threads:
    urlpatterns += patterns("",
        url(r'^reply/(?P<cid>[\d]+)$',   views.reply,   name='comments-xtd-reply'),
    )

