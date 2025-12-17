from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path

from django_comments_xtd.tests import views

urlpatterns = [
    path("accounts/login/", auth_views.LoginView.as_view()),
    re_path(
        r"^articles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        r"(?P<slug>[-\w]+)/$",
        views.dummy_view,
        name="article-detail",
    ),
    re_path(
        r"^diary/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/",
        views.dummy_view,
        name="diary-detail",
    ),
    # ------------------------------------------------------------------
    # Remap url `comments-xtd-comment-reaction-authors` with alternative
    # view that overwrites the pagination_class, so that it does not
    # paginate:
    #
    re_path(
        r"^(?P<comment_pk>[\d]+)/(?P<reaction_value>[\w\+\-]+)/$",
        views.AltCommentReactionAuthorsList.as_view(),
        name="comments-xtd-comment-reaction-authors",
    ),
    # ------------------------------------------------------------------
    path("comments/", include("django_comments_xtd.urls")),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
]
urlpatterns += staticfiles_urlpatterns()
