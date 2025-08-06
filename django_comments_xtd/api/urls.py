from django.urls import path, re_path

from django_comments_xtd.api.views import (
    CommentCount,
    CommentCreate,
    CommentList,
    CreateReportFlag,
    PreviewUserAvatar,
    ToggleFeedbackFlag,
)

urlpatterns = [
    path("comment/", CommentCreate.as_view(), name="comments-xtd-api-create"),
    path(
        "preview/", PreviewUserAvatar.as_view(), name="comments-xtd-api-preview"
    ),
    re_path(
        r"^(?P<content_type>\w+-\w+)/(?P<object_pk>[-\w]+)/$",
        CommentList.as_view(),
        name="comments-xtd-api-list",
    ),
    re_path(
        r"^(?P<content_type>\w+-\w+)/(?P<object_pk>[-\w]+)/count/$",
        CommentCount.as_view(),
        name="comments-xtd-api-count",
    ),
    path(
        "feedback/",
        ToggleFeedbackFlag.as_view(),
        name="comments-xtd-api-feedback",
    ),
    path("flag/", CreateReportFlag.as_view(), name="comments-xtd-api-flag"),
]
