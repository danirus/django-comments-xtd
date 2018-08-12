from __future__ import unicode_literals

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from django_comments_xtd import django_comments
from django_comments_xtd.api.views import CommentCreate
from django_comments_xtd.tests.models import Article, Diary


request_factory = APIRequestFactory()


def post_comment(data, auth_user=None):
    request = request_factory.post(reverse('comments-xtd-api-create'), data)
    if auth_user:
        force_authenticate(request, user=auth_user)
    view = CommentCreate.as_view()
    return view(request)


class CommentCreateTestCase(TestCase):
    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.form = django_comments.get_form()(self.article)

    def test_post_returns_2xx_response(self):
        data = {"name": "Bob", "email": "fulanito@detal.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.mock_mailer.call_count, 1)

    def test_post_returns_4xx_response(self):
        # It uses an authenticated user, but the user has no mail address.
        self.user = User.objects.create_user("bob", "", "pwd")
        data = {"name": "", "email": "",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data, auth_user=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('name' in response.data)
        self.assertTrue('email' in response.data)
        self.assertEqual(self.mock_mailer.call_count, 0)
