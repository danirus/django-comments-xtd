from django.urls import path, re_path

from .views import (
    CommentCount,
    CommentCreate,
    CommentList,
    CommentReactionAuthorsList,
    CreateReportFlag,
    PostCommentReaction,
)

urlpatterns = [
    path("comment/", CommentCreate.as_view(), name="comments-xtd-api-create"),
    path(
        "react/",
        PostCommentReaction.as_view(),
        name="comments-xtd-api-react",
    ),
    path("flag/", CreateReportFlag.as_view(), name="comments-xtd-api-flag"),
    re_path(
        r"^(?P<comment_pk>[\d]+)/(?P<reaction_value>[\w\+\-]+)/$",
        CommentReactionAuthorsList.as_view(),
        name="comments-xtd-comment-reaction-authors",
    ),
    # -----------------------------------------------------------------
    # The following 3 re_path entries read the content type as
    # <applabel>-<model>, and the object ID to which comments
    # have been sent.
    # List the comments sent to the <ctype>/<object_pk>.
    re_path(
        r"^(?P<content_type>\w+[-]{1}\w+)/(?P<object_pk>[-\w]+)/$",
        CommentList.as_view(),
        name="comments-xtd-api-list",
    ),
    # Number of comments sent to the <ctype>/<object_pk>.
    re_path(
        r"^(?P<content_type>\w+[-]{1}\w+)/(?P<object_pk>[-\w]+)/count/$",
        CommentCount.as_view(),
        name="comments-xtd-api-count",
    ),
]
