from django.urls import include, re_path

from rest_framework.urlpatterns import format_suffix_patterns

from django_comments_xtd import api, views

urlpatterns = [
    re_path(r'^sent/$', views.sent, name='comments-xtd-sent'),
    re_path(r'^confirm/(?P<key>[^/]+)/$', views.confirm,
            name='comments-xtd-confirm'),
    re_path(r'^mute/(?P<key>[^/]+)/$', views.mute, name='comments-xtd-mute'),
    re_path(r'^reply/(?P<cid>[\d]+)/$', views.reply, name='comments-xtd-reply'),

    # Remap comments-flag to check allow-flagg<ing is enabled.
    re_path(r'^flag/(\d+)/$', views.flag, name='comments-flag'),
    # New flags in addition to those provided by django-contrib-comments.
    re_path(r'^like/(\d+)/$', views.like, name='comments-xtd-like'),
    re_path(r'^liked/$', views.like_done, name='comments-xtd-like-done'),
    re_path(r'^dislike/(\d+)/$', views.dislike, name='comments-xtd-dislike'),
    re_path(r'^disliked/$', views.dislike_done,
            name='comments-xtd-dislike-done'),

    # API handlers.
    re_path(r'^api/comment/$', api.CommentCreate.as_view(),
            name='comments-xtd-api-create'),
    re_path(r'^api/preview/$', api.preview_user_avatar,
            name='comments-xtd-api-preview'),
    re_path(r'^api/(?P<content_type>\w+[-]{1}\w+)/(?P<object_pk>[-\w]+)/$',
            api.CommentList.as_view(), name='comments-xtd-api-list'),
    re_path(
        r'^api/(?P<content_type>\w+[-]{1}\w+)/(?P<object_pk>[-\w]+)/count/$',
        api.CommentCount.as_view(), name='comments-xtd-api-count'),
    re_path(r'^api/feedback/$', api.ToggleFeedbackFlag.as_view(),
            name='comments-xtd-api-feedback'),
    re_path(r'^api/flag/$', api.CreateReportFlag.as_view(),
            name='comments-xtd-api-flag'),

    re_path(r'', include("django_comments.urls")),
]


urlpatterns = format_suffix_patterns(urlpatterns)
