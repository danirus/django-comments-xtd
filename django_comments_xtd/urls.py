from django.urls import re_path
from django_comments.views.comments import comment_done
from django_comments.views.moderation import (
    approve,
    approve_done,
    delete,
    delete_done,
    flag_done,
)
from rest_framework.urlpatterns import format_suffix_patterns

from django_comments_xtd import views

urlpatterns = [
    re_path(
        r"^post/$",
        views.PostCommentView.as_view(),
        name="comments-xtd-post-comment",
    ),
    re_path(r"^posted/$", comment_done, name="comments-comment-done"),
    re_path(r"^sent/$", views.sent, name="comments-xtd-sent"),
    re_path(
        r"^confirm/(?P<key>[^/]+)/$",
        views.confirm,
        name="comments-xtd-confirm",
    ),
    re_path(
        r"^mute/(?P<key>[^/]+)/$",
        views.MuteCommentView.as_view(),
        name="comments-xtd-mute",
    ),
    re_path(
        r"^reply/(?P<cid>\d+)/$",
        views.ReplyCommentView.as_view(),
        name="comments-xtd-reply",
    ),
    # Remap comments-flag to check allow-flagging is enabled.
    re_path(
        r"^flag/(\d+)/$", views.FlagCommentView.as_view(), name="comments-flag"
    ),
    re_path(r"^flagged/$", flag_done, name="comments-flag-done"),
    re_path(r"^delete/(\d+)/$", delete, name="comments-delete"),
    re_path(r"^deleted/$", delete_done, name="comments-delete-done"),
    re_path(r"^approve/(\d+)/$", approve, name="comments-approve"),
    re_path(r"^approved/$", approve_done, name="comments-approve-done"),
    re_path(
        r"^vote/(\d+)/$",
        views.VoteOnCommentView.as_view(),
        name="comments-xtd-vote",
    ),
    re_path(
        r"^voted/$",
        views.VoteOnCommentDoneView.as_view(),
        name="comments-xtd-vote-done",
    ),
    re_path(
        r"^react/(\d+)/$",
        views.ReactToCommentView.as_view(),
        name="comments-xtd-react",
    ),
    re_path(
        r"^reacted/$",
        views.ReactToCommentDoneView.as_view(),
        name="comments-xtd-react-done",
    ),
    re_path(
        r"^reaction-user-list/(\d+)/([\w\+\-]+)/$",
        views.CommentReactionUserListView.as_view(),
        name="comments-xtd-reaction-user-list",
    ),
    re_path(
        r"^cr/(\d+)/(\d+)/(\d+)/$",
        views.CommentUrlView.as_view(),
        name="comments-url-redirect",
    ),
    # API handlers.
    # path(
    #     "api/",
    #     include("django_comments_xtd.api.urls"),
    #     {"override_drf_defaults": settings.COMMENTS_XTD_OVERRIDE_DRF_DEFAULTS},
    # ),
]


urlpatterns = format_suffix_patterns(urlpatterns)
