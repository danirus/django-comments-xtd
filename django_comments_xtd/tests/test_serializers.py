from __future__ import unicode_literals

from datetime import datetime
import pytz
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
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
                "followup": True, "reply_to": 0,
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


def get_fake_avatar(comment):
    return f"/fake/avatar/{comment.user.username}"


funcpath = "django_comments_xtd.tests.test_serializers.get_fake_avatar"


class ReadCommentsGetUserAvatarTestCase(TestCase):
    # Test ReadCommentSerializer method get_user_avatar.
    # Change setting COMMENTS_XTD_API_GET_USER_AVATAR so that it uses a
    # deterministic function: get_fake_avatar (here defined). Then send a
    # couple of comments and verify that the function is called.

    def setUp(self):
        joe = User.objects.create_user("joe", "joe@example.com", "joepwd",
                                       first_name="Joe", last_name="Bloggs")
        alice = User.objects.create_user("alice", "alice@tal.com", "alicepwd",
                                         first_name="Alice", last_name="Bloggs")
        self.article = Article.objects.create(title="September",
                                              slug="september",
                                              body="During September...")
        self.article_ct = ContentType.objects.get(app_label="tests",
                                                  model="article")
        self.site = Site.objects.get(pk=1)

        # Testing comment from Bob.
        XtdComment.objects.create(content_type=self.article_ct,
                                  object_pk=self.article.id,
                                  content_object=self.article,
                                  site=self.site,
                                  comment="testing comment from Bob",
                                  user=joe,
                                  submit_date=datetime.now())

        # Testing comment from Alice.
        XtdComment.objects.create(content_type=self.article_ct,
                                  object_pk=self.article.id,
                                  content_object=self.article,
                                  site=self.site,
                                  comment="testing comment from Alice",
                                  user=alice,
                                  submit_date=datetime.now())

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_API_GET_USER_AVATAR=funcpath)
    def test_setting_COMMENTS_XTD_API_GET_USER_AVATAR_works(self):
        qs = XtdComment.objects.all()
        ser = ReadCommentSerializer(qs, context={"request": None}, many=True)
        self.assertEqual(ser.data[0]['user_avatar'], '/fake/avatar/joe')
        self.assertEqual(ser.data[1]['user_avatar'], '/fake/avatar/alice')


class RenderSubmitDateTestCase(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="October", slug="october",
                                              body="What I did on October...")

    def create_comment(self, submit_date_is_aware=True):
        site = Site.objects.get(pk=1)
        ctype = ContentType.objects.get(app_label="tests", model="article")
        if submit_date_is_aware:
            utc = pytz.timezone("UTC")
            submit_date = datetime(2021, 1, 10, 10, 15, tzinfo=utc)
        else:
            submit_date = datetime(2021, 1, 10, 10, 15)
        self.cm = XtdComment.objects.create(content_type=ctype,
                                            object_pk=self.article.id,
                                            content_object=self.article,
                                            site=site, name="Joe Bloggs",
                                            email="joe@bloggs.com",
                                            comment="Just a comment",
                                            submit_date=submit_date)

    @patch.multiple('django.conf.settings', USE_TZ=False)
    @patch.multiple('django_comments_xtd.conf.settings', USE_TZ=False)
    def test_submit_date_when_use_tz_is_false(self):
        self.create_comment(submit_date_is_aware=False)
        qs = XtdComment.objects.all()
        ser = ReadCommentSerializer(qs, context={"request": None}, many=True)
        self.assertEqual(ser.data[0]['submit_date'],
                         'Jan. 10, 2021, 10:15 a.m.')

    @patch.multiple('django.conf.settings', USE_TZ=True)
    @patch.multiple('django_comments_xtd.conf.settings', USE_TZ=True)
    def test_submit_date_when_use_tz_is_true(self):
        self.create_comment(submit_date_is_aware=True)
        qs = XtdComment.objects.all()
        ser = ReadCommentSerializer(qs, context={"request": None}, many=True)
        self.assertEqual(ser.data[0]['submit_date'],
                         'Jan. 10, 2021, 11:15 a.m.')
