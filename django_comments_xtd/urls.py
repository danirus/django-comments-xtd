from django.conf.urls import include, url

from django_comments_xtd import views
from django_comments_xtd.conf import settings


urlpatterns = [
    url(r'', include("django_comments.urls")),
    url(r'^sent/$', views.sent, name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm,
        name='comments-xtd-confirm'),
    url(r'^mute/(?P<key>[^/]+)$', views.mute, name='comments-xtd-mute'),

    # New flags in addition to those provided by django-contrib-comments.
    url(r'^like/(\d+)/$', views.like, name='comments-xtd-like'),
    url(r'^liked/$', views.like_done, name='comments-xtd-like-done'),
    url(r'^dislike/(\d+)/$', views.dislike, name='comments-xtd-dislike'),
    url(r'^disliked/$', views.dislike_done, name='comments-xtd-dislike-done'),
]


if settings.COMMENTS_XTD_MAX_THREAD_LEVEL > 0:
    urlpatterns.append(
        url(r'^reply/(?P<cid>[\d]+)$', views.reply, name='comments-xtd-reply')
    )
