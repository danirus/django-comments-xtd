from __future__ import unicode_literals

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from django_comments_xtd import django_comments
from django_comments_xtd.api.serializers import ReadCommentSerializer
from django_comments_xtd.models import XtdComment
from django_comments_xtd.signals import should_request_be_authorized
from django_comments_xtd.tests.models import (
    Article, authorize_api_post_comment
)
from django_comments_xtd.tests.utils import post_comment


class UserModeratorTestCase(TestCase):
    # Test ReadCommentSerializer.user_moderator field.

    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.form = django_comments.get_form()(self.article)

    def _create_user(self, can_moderate=False):
        bob = User.objects.create_user("joe", "fulanito@detal.com", "pwd",
                                       first_name="Joe", last_name="Bloggs")
        if can_moderate:
            ct = ContentType.objects.get(app_label="django_comments",
                                         model="comment")
            permission = Permission.objects.get(content_type=ct,
                                                codename="can_moderate")
            bob.user_permissions.add(permission)
        return bob

    def _send_auth_comment(self, user):
        data = {"name": "", "email": "",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data, auth_user=user)
        self.assertEqual(response.status_code, 201)

    def test_user_moderator_is_False(self):
        bob = self._create_user(can_moderate=False)
        self._send_auth_comment(bob)

        # Fetch the comment, serialize it and check user_moderator field.
        xtdcomment = XtdComment.objects.get(pk=1)
        context = {"request": {"user": bob}}
        ser = ReadCommentSerializer(xtdcomment, context=context)
        self.assertFalse(ser.data['user_moderator'])

    def test_user_moderator_is_True(self):
        bob = self._create_user(can_moderate=True)
        self._send_auth_comment(bob)

        # Fetch the comment, serialize it and check user_moderator field.
        xtdcomment = XtdComment.objects.get(pk=1)
        context = {"request": {"user": bob}}
        ser = ReadCommentSerializer(xtdcomment, context=context)
        self.assertTrue(ser.data['user_moderator'])


class PostCommentAsVisitorTestCase(TestCase):
    # Test WriteCommentSerializer as a mere visitor. The function in 
    # authorize_api_post_comment in `test/models.py` is not listening for 
    # the signal `should_request_be_authorized` yet. Therefore before
    # connecting the signal with the function the post comment must fail
    # indicating missing fields (timestamp, security_hash and honeypot).

    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.form = django_comments.get_form()(self.article)
        # Remove the following fields on purpose, as we don't know them and
        # therefore we don't send them when using the web API (unless when)
        # using the JavaScript plugin, but that is not the case being tested 
        # here.
        for field_name in ['security_hash', 'timestamp']:
            self.form.initial.pop(field_name)

    def test_post_comment_as_visitor_before_connecting_signal(self):
        data = {
            "name": "Joe Bloggs", "email": "joe@bloggs.com", "followup": True, 
            "reply_to": 0, "comment": "This post comment request should fail"
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.rendered_content, 
            b'{"detail":"You do not have permission to perform this action."}'
        )
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_post_comment_as_visitor_after_connecting_signal(self):
        should_request_be_authorized.connect(authorize_api_post_comment)
        data = {
            "name": "Joe Bloggs", "email": "joe@bloggs.com", "followup": True, 
            "reply_to": 0, "comment": "This post comment request should fail"
        }
        data.update(self.form.initial)
        client = APIClient()
        token = "Token 08d9fd42468aebbb8087b604b526ff0821ce4525";
        client.credentials(HTTP_AUTHORIZATION=token)
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse('comments-xtd-api-create'), data)
        self.assertEqual(response.status_code, 204)  # Confirmation req sent.
        self.assertTrue(self.mock_mailer.call_count == 1)

    def test_post_comment_as_registered_user_after_connecting_signal(self):
        bob = User.objects.create_user("joe", "fulanito@detal.com", "pwd",
                                       first_name="Joe", last_name="Bloggs")

        should_request_be_authorized.connect(authorize_api_post_comment)
        data = {
            "name": "Joe Bloggs", "email": "joe@bloggs.com", "followup": True, 
            "reply_to": 0, "comment": "This post comment request should fail"
        }
        data.update(self.form.initial)
        client = APIClient()
        client.login(username='joe', password='pwd')
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse('comments-xtd-api-create'), data)
        self.assertEqual(response.status_code, 201)  # Comment created.
        self.assertTrue(self.mock_mailer.call_count == 0)
