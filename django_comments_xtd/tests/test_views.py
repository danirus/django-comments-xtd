from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from django_comments_xtd.views import PostCommentView, confirm

request_factory = RequestFactory()


def post_article_comment(data, article, auth_user=None):
    request = request_factory.post(
        reverse(
            "article-detail",
            kwargs={
                "year": article.publish.year,
                "month": article.publish.month,
                "day": article.publish.day,
                "slug": article.slug,
            },
        ),
        data=data,
        follow=True,
    )
    if auth_user:
        request.user = auth_user
    else:
        request.user = AnonymousUser()
    request._dont_enforce_csrf_checks = True
    return PostCommentView.as_view()(request)


def post_diary_comment(data, diary_entry, auth_user=None):
    request = request_factory.post(
        reverse(
            "diary-detail",
            kwargs={
                "year": diary_entry.publish.year,
                "month": diary_entry.publish.month,
                "day": diary_entry.publish.day,
            },
        ),
        data=data,
        follow=True,
    )
    if auth_user:
        request.user = auth_user
    else:
        request.user = AnonymousUser()
    request._dont_enforce_csrf_checks = True
    return PostCommentView.as_view()(request)


def confirm_comment_url(key, follow=True):
    request = request_factory.get(
        reverse("comments-xtd-confirm", kwargs={"key": key}), follow=follow
    )
    request.user = AnonymousUser()
    return confirm(request, key)
