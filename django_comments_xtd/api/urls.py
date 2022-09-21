from django.urls import path, re_path

from .views import (
    CommentCount, CommentCreate, CommentList,
    CreateReportFlag, ToggleFeedbackFlag,
    preview_user_avatar,
)

urlpatterns = [
    path('comment/', CommentCreate.as_view(),
         name='comments-xtd-api-create'),
    path('preview/', preview_user_avatar,
         name='comments-xtd-api-preview'),
    re_path(r'^(?P<content_type>\w+-\w+)/(?P<object_pk>[-\w]+)/$',
            CommentList.as_view(), name='comments-xtd-api-list'),
    re_path(
        r'^(?P<content_type>\w+-\w+)/(?P<object_pk>[-\w]+)/count/$',
        CommentCount.as_view(), name='comments-xtd-api-count'),
    path('feedback/', ToggleFeedbackFlag.as_view(),
         name='comments-xtd-api-feedback'),
    path('flag/', CreateReportFlag.as_view(),
         name='comments-xtd-api-flag'),
]
