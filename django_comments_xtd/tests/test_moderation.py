from __future__ import unicode_literals

import re

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_comments_xtd import django_comments
from django_comments_xtd.tests.models import Diary


send_mail = ''  # string to send_mail function to patch
try:
    import imp
    imp.find_module('django_comments')
    send_mail = 'django_comments.moderation.send_mail'
except ImportError:
    send_mail = 'django.contrib.comments.moderation.send_mail'


class ModeratorApprovesComment(TestCase):
    def setUp(self):
        patcher_app1 = patch(send_mail)
        patcher_app2 = patch('django_comments_xtd.views.send_mail')
        self.mailer_app1 = patcher_app1.start()
        self.mailer_app2 = patcher_app2.start()
        diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now())
        self.form = django_comments.get_form()(diary_entry)

    def post_valid_data(self):
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data, follow=True)

    def get_confirm_comment_url(self, key):
        self.response = self.client.get(reverse("comments-xtd-confirm",
                                                kwargs={'key': key}),
                                        follow=True)

    def test_moderation_with_registered_user(self):
        User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        self.assert_(self.mailer_app1.call_count == 0)
        self.post_valid_data()
        # Moderation class:
        # django_comments_xtd.tests.models.DiaryCommentModerator
        # must trigger an email once comment has passed moderation.
        self.assert_(self.mailer_app1.call_count == 1)
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        self.assert_(comment.is_public is True)

    def test_moderation_with_unregistered_user(self):
        self.post_valid_data()
        self.assert_(self.mailer_app1.call_count == 0)
        self.assert_(self.mailer_app2.call_count == 1)
        mail_msg = self.mailer_app2.call_args[0][1]
        key = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                            mail_msg).group("key"))
        self.get_confirm_comment_url(key)
        self.assert_(self.mailer_app1.call_count == 1)
        self.assert_(self.mailer_app2.call_count == 1)
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        self.assert_(comment.is_public is True)


class ModeratorHoldsComment(TestCase):
    def setUp(self):
        patcher_app1 = patch(send_mail)
        patcher_app2 = patch('django_comments_xtd.views.send_mail')
        self.mailer_app1 = patcher_app1.start()
        self.mailer_app2 = patcher_app2.start()
        diary_entry = Diary.objects.create(
            body="What I did Yesterday...",
            allow_comments=True,
            publish=datetime.now() - timedelta(days=5))
        self.form = django_comments.get_form()(diary_entry)

    def post_valid_data(self):
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data, follow=True)

    def get_confirm_comment_url(self, key):
        self.response = self.client.get(reverse("comments-xtd-confirm",
                                                kwargs={'key': key}),
                                        follow=True)

    def test_moderation_with_registered_user(self):
        User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        self.post_valid_data()
        # Moderation class:
        # django_comments_xtd.tests.models.DiaryCommentModerator
        # must trigger an email once comment has passed moderation.
        self.assert_(self.mailer_app1.call_count == 1)
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        self.assert_(comment.is_public is False)

    def test_moderation_with_unregistered_user(self):
        self.post_valid_data()
        self.assert_(self.mailer_app1.call_count == 0)
        self.assert_(self.mailer_app2.call_count == 1)
        mail_msg = self.mailer_app2.call_args[0][1]
        key = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                            mail_msg).group("key"))
        self.get_confirm_comment_url(key)
        self.assert_(self.mailer_app1.call_count == 1)
        self.assert_(self.mailer_app2.call_count == 1)
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        self.assert_(comment.is_public is False)
