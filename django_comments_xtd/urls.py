from django.urls import re_path

from rest_framework.urlpatterns import format_suffix_patterns
from django_comments.views.comments import comment_done
from django_comments.views.moderation import (flag_done, delete, delete_done,
                                              approve, approve_done)

from django_comments_xtd import views


urlpatterns = [
    re_path(r'^post/$', views.post, name='comments-xtd-post'),
    re_path(r'^posted/$', comment_done, name='comments-comment-done'),

    re_path(r'^sent/$', views.sent, name='comments-xtd-sent'),
    re_path(r'^confirm/(?P<key>[^/]+)/$', views.confirm,
            name='comments-xtd-confirm'),
    re_path(r'^mute/(?P<key>[^/]+)/$', views.mute, name='comments-xtd-mute'),
    re_path(r'^reply/(?P<cid>[\d]+)/$', views.reply, name='comments-xtd-reply'),

    # Remap comments-flag to check allow-flagging is enabled.
    re_path(r'^flag/(\d+)/$', views.flag, name='comments-flag'),
    re_path(r'^flagged/$', flag_done, name='comments-flag-done'),

    re_path(r'^delete/(\d+)/$', delete, name='comments-delete'),
    re_path(r'^deleted/$', delete_done, name='comments-delete-done'),
    re_path(r'^approve/(\d+)/$', approve, name='comments-approve'),
    re_path(r'^approved/$', approve_done, name='comments-approve-done'),

    # New flags in addition to those provided by django-contrib-comments.
    re_path(r'^react/(\d+)/$', views.react, name='comments-xtd-react'),
    re_path(r'^reacted/$', views.react_done, name='comments-xtd-react-done'),

    # Remap comments-url-redirect to add query string with page number.
    re_path(r'^cr/(\d+)/(\d+)/(\d+)/$', views.comment_in_page,
            name='comments-url-redirect'),

    # API handlers.
    path('api/', include("django_comments_xtd.api.urls"),
         {'override_drf_defaults': True}),

    path('', include("django_comments.urls")),
]


urlpatterns = format_suffix_patterns(urlpatterns)
