from django.conf.urls import include, url

from django_comments_xtd import views


urlpatterns = [
    url(r'', include("django_comments.urls")),
    url(r'^sent/$', views.sent, name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm,
        name='comments-xtd-confirm'),
    url(r'^mute/(?P<key>[^/]+)$', views.mute, name='comments-xtd-mute'),
    url(r'^reply/(?P<cid>[\d]+)$', views.reply, name='comments-xtd-reply'),

    # New flags in addition to those provided by django-contrib-comments.
    url(r'^like/(\d+)/$', views.like, name='comments-xtd-like'),
    url(r'^liked/$', views.like_done, name='comments-xtd-like-done'),
    url(r'^dislike/(\d+)/$', views.dislike, name='comments-xtd-dislike'),
    url(r'^disliked/$', views.dislike_done, name='comments-xtd-dislike-done'),
]
