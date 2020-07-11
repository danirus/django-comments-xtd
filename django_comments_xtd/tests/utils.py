from django.urls import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from django_comments_xtd.api.views import CommentCreate


request_factory = APIRequestFactory()


def post_comment(data, auth_user=None):
    request = request_factory.post(reverse('comments-xtd-api-create'), data)
    if auth_user:
        force_authenticate(request, user=auth_user)
    view = CommentCreate.as_view()
    return view(request)
