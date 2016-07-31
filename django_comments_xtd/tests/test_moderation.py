from __future__ import unicode_literals

import re

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from datetime import datetime, timedelta

import django
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

try:
    from django_comments.models import CommentFlag
except ImportError:
    from django.contrib.comments.models import CommentFlag

from django_comments_xtd import django_comments
from django_comments_xtd.models import LIKEDIT_FLAG, DISLIKEDIT_FLAG
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


class FlaggingRemovalSuggestion(TestCase):
    """Scenario to test the flag removal_suggestion_notification"""

    def setUp(self):
        patcher = patch('django_comments_xtd.moderation.send_mail')
        self.mailer = patcher.start()
        diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now())
        self.form = django_comments.get_form()(diary_entry)
        User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data, follow=True)

    def test_anonymous_user_redirected_when_flagging(self):
        self.client.logout()
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        flag_url = reverse("comments-flag", args=[comment.id])
        response = self.client.get(flag_url, follow=True)
        dest_url = '/accounts/login/?next=/comments/flag/1/'
        self.assertRedirects(response, dest_url)

    def test_loggedin_user_can_flag_comment(self):
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        flag_url = reverse("comments-flag", args=[comment.id])
        response = self.client.get(flag_url)
        self.assertTemplateUsed(response, 'comments/flag.html')
        response = self.client.post(flag_url)
        self.assertRedirects(response, reverse("comments-flag-done") + "?c=1")
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=CommentFlag.SUGGEST_REMOVAL)
        self.assert_(flags.count() == 1)

    def test_email_is_triggered(self):
        flag_url = reverse("comments-flag", args=[1])
        self.assert_(self.mailer.call_count == 0)
        self.client.post(flag_url)
        self.assert_(self.mailer.call_count == 1)


class FlaggingLikedItAndDislikedit(TestCase):
    """Scenario to test the flag removal_suggestion_notification"""

    def setUp(self):
        diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now())
        self.form = django_comments.get_form()(diary_entry)
        User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data, follow=True)

    def test_anonymous_user_is_redirected(self):
        self.client.logout()
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        response = self.client.get(like_url, follow=True)
        dest_url = '/accounts/login/?next=/comments/like/1/'
        self.assertRedirects(response, dest_url)
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        response = self.client.get(dislike_url, follow=True)
        dest_url = '/accounts/login/?next=/comments/dislike/1/'
        self.assertRedirects(response, dest_url)

    def test_loggedin_user_can_like(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        response = self.client.get(like_url)
        self.assertTemplateUsed(response, 'django_comments_xtd/like.html')
        response = self.client.post(like_url)
        self.assertRedirects(response,
                             reverse("comments-xtd-like-done") + "?c=1")
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 1)

    def test_loggedin_user_can_dislike(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        response = self.client.get(dislike_url)
        self.assertTemplateUsed(response, 'django_comments_xtd/dislike.html')
        response = self.client.post(dislike_url)
        self.assertRedirects(response,
                             reverse("comments-xtd-dislike-done") + "?c=1")
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 1)

    def test_likedit_can_be_cancelled(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        self.client.post(like_url)
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 1)
        # Now we liked the comment again to cancel the flag.
        self.client.post(like_url)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 0)

    def test_dislikedit_can_be_cancelled(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        self.client.post(dislike_url, follow=True)
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 1)
        # Now we liked the comment again to cancel the flag.
        self.client.post(dislike_url)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 0)

    def test_likedit_cancels_dislikedit(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        self.client.post(dislike_url)
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 1)
        # Now we liked the comment again to cancel the flag.
        like_url = reverse("comments-xtd-like", args=[comment.id])
        self.client.post(like_url)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 0)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 1)

    def test_dislikedit_cancels_likedit(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        self.client.post(like_url)
        user = User.objects.get(username='bob')
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 1)
        # Now we liked the comment again to cancel the flag.
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        self.client.post(dislike_url)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=LIKEDIT_FLAG)
        self.assert_(flags.count() == 0)
        flags = CommentFlag.objects.filter(comment=comment,
                                           user=user,
                                           flag=DISLIKEDIT_FLAG)
        self.assert_(flags.count() == 1)
