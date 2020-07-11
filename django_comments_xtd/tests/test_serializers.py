from __future__ import unicode_literals

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_comments_xtd import django_comments
from django_comments_xtd.api.serializers import ReadCommentSerializer
from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article
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
