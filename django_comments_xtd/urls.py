from django.conf.urls import include, url

from rest_framework.urlpatterns import format_suffix_patterns

from django_comments_xtd import api, views

urlpatterns = [
    url(r'', include("django_comments.urls")),
    url(r'^sent/$', views.sent, name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)/$', views.confirm,
        name='comments-xtd-confirm'),
    url(r'^mute/(?P<key>[^/]+)/$', views.mute, name='comments-xtd-mute'),
    url(r'^reply/(?P<cid>[\d]+)/$', views.reply, name='comments-xtd-reply'),

    # New flags in addition to those provided by django-contrib-comments.
    url(r'^like/(\d+)/$', views.like, name='comments-xtd-like'),
    url(r'^liked/$', views.like_done, name='comments-xtd-like-done'),
    url(r'^dislike/(\d+)/$', views.dislike, name='comments-xtd-dislike'),
    url(r'^disliked/$', views.dislike_done, name='comments-xtd-dislike-done'),

    # API handlers.
    url(r'^api/(?P<content_type>\w+[-]{1}\w+)/(?P<object_pk>[0-9]+)/$',
        api.CommentCreateList.as_view(), name='comments-xtd-api-list'),
    url(r'^api/feedback/$', api.ToggleFeedbackFlag.as_view(),
        name='comments-xtd-api-feedback'),
    url(r'^api/flag/$', api.CreateReportFlag.as_view(),
        name='comments-xtd-api-flag'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
