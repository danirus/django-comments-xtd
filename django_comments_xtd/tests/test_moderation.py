from __future__ import unicode_literals
from django_comments_xtd.models import XtdComment

import importlib
import re
from unittest.mock import patch
from datetime import datetime, timedelta

from django.contrib.auth.models import AnonymousUser, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory
from django.urls import reverse
import pytest

import django_comments
from django_comments.models import Comment, CommentFlag
from django_comments.views.moderation import delete

from django_comments_xtd import views
from django_comments_xtd.tests.models import (
    Article,
    Diary,
    DiaryCommentModerator,
)
from django_comments_xtd.tests.test_views import (
    confirm_comment_url,
    post_article_comment,
    post_diary_comment,
)

request_factory = RequestFactory()


send_mail = ""  # string to send_mail function to patch


if importlib.util.find_spec("django_comments"):
    send_mail = "django_comments.moderation.send_mail"
else:
    send_mail = "django.contrib.comments.moderation.send_mail"


class ModeratorApprovesComment(TestCase):
    def setUp(self):
        patcher_app1 = patch(send_mail)
        patcher_app2 = patch("django_comments_xtd.views.send_mail")
        self.mailer_app1 = patcher_app1.start()
        self.mailer_app2 = patcher_app2.start()
        self.diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now(),
        )
        self.form = django_comments.get_form()(self.diary_entry)

    def post_valid_data(self, auth_user=None):
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
        }
        data.update(self.form.initial)
        response = post_diary_comment(
            data, self.diary_entry, auth_user=auth_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/posted/?c="))

    def test_moderation_with_registered_user(self):
        user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.assertTrue(self.mailer_app1.call_count == 0)
        self.post_valid_data(user)
        # Moderation class:
        # django_comments_xtd.tests.models.DiaryCommentModerator
        # must trigger an email once comment has passed moderation.
        self.assertTrue(self.mailer_app1.call_count == 1)
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        self.assertTrue(comment.is_public is True)

    def test_moderation_with_unregistered_user(self):
        self.post_valid_data()
        self.assertTrue(self.mailer_app1.call_count == 0)
        self.assertTrue(self.mailer_app2.call_count == 1)
        mail_msg = self.mailer_app2.call_args[0][1]
        key = str(
            re.search(r"http://.+/confirm/(?P<key>[\S]+)/", mail_msg).group(
                "key"
            )
        )
        confirm_comment_url(key)
        self.assertTrue(self.mailer_app1.call_count == 1)
        self.assertTrue(self.mailer_app2.call_count == 1)
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        self.assertTrue(comment.is_public is True)


class ModeratorHoldsComment(TestCase):
    def setUp(self):
        patcher_app1 = patch(send_mail)
        patcher_app2 = patch("django_comments_xtd.views.send_mail")
        self.mailer_app1 = patcher_app1.start()
        self.mailer_app2 = patcher_app2.start()
        self.diary_entry = Diary.objects.create(
            body="What I did Yesterday...",
            allow_comments=True,
            publish=datetime.now() - timedelta(days=5),
        )
        self.form = django_comments.get_form()(self.diary_entry)

    def post_valid_data(self, auth_user=None):
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
        }
        data.update(self.form.initial)
        response = post_diary_comment(
            data, self.diary_entry, auth_user=auth_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/posted/?c="))

    def test_moderation_with_registered_user(self):
        user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.assertTrue(self.mailer_app1.call_count == 0)
        self.post_valid_data(user)
        # Moderation class:
        # django_comments_xtd.tests.models.DiaryCommentModerator
        # must trigger an email once comment has passed moderation.
        self.assertTrue(self.mailer_app1.call_count == 1)
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        self.assertTrue(comment.is_public is False)

    def test_moderation_with_unregistered_user(self):
        self.post_valid_data()
        self.assertTrue(self.mailer_app1.call_count == 0)
        self.assertTrue(self.mailer_app2.call_count == 1)
        mail_msg = self.mailer_app2.call_args[0][1]
        key = str(
            re.search(r"http://.+/confirm/(?P<key>[\S]+)/", mail_msg).group(
                "key"
            )
        )
        confirm_comment_url(key)
        self.assertTrue(self.mailer_app1.call_count == 1)
        self.assertTrue(self.mailer_app2.call_count == 1)
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        self.assertTrue(comment.is_public is False)


app_model_options_mock = {
    "tests.article": {
        "comment_flagging_enabled": True,
        "comment_reactions_enabled": False,
        "object_reactions_enabled": False,
    }
}


class FlaggingRemovalSuggestion(TestCase):
    """Scenario to test the flag removal_suggestion_notification"""

    def setUp(self):
        patcher = patch("django_comments_xtd.moderation.send_mail")
        self.mailer = patcher.start()
        diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now(),
        )
        self.user = User.objects.create_user("bob", "bob@example.com", "pwd")
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
        }
        form = django_comments.get_form()(diary_entry)
        data.update(form.initial)
        post_diary_comment(data, diary_entry, auth_user=self.user)
        # Also create an article and a comment to that article,
        # To test that flagging a comment of a model not registered
        # for moderation does not trigger the notify_removal_suggestion.
        article_entry = Article.objects.create(
            title="September", slug="september", body="During September..."
        )
        form = django_comments.get_form()(article_entry)
        data.update(form.initial)
        post_article_comment(data, article_entry, auth_user=self.user)
        self.cmts = XtdComment.objects.all()

    def test_anonymous_user_redirected_when_flagging(self):
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        flag_url = reverse("comments-flag", args=[comment.id])
        request = request_factory.get(flag_url)
        request.user = AnonymousUser()
        response = views.flag(request, comment.id)
        dest_url = "/accounts/login/?next=/comments/flag/1/"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, dest_url)

    def test_loggedin_user_can_flag_comment(self):
        comment = django_comments.get_model().objects.for_app_models(
            "tests.diary"
        )[0]
        flag_url = reverse("comments-flag", args=[comment.id])
        request = request_factory.get(flag_url)
        request.user = self.user
        response = views.flag(request, comment.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find(b"Flag comment") > -1)
        request = request_factory.post(flag_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.flag(request, comment.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("comments-flag-done") + "?c=1")
        flags = CommentFlag.objects.filter(
            comment=comment, user=self.user, flag=CommentFlag.SUGGEST_REMOVAL
        )
        self.assertTrue(flags.count() == 1)

    def test_email_is_triggered(self):
        flag_url = reverse("comments-flag", args=[1])
        self.assertTrue(self.mailer.call_count == 0)
        request = request_factory.post(flag_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        views.flag(request, 1)
        self.assertTrue(self.mailer.call_count == 1)

    def test_no_email_when_notify_removal_suggestion_is_None(self):
        with patch.object(
            DiaryCommentModerator, "removal_suggestion_notification", None
        ):
            flag_url = reverse("comments-flag", args=[1])
            self.assertTrue(self.mailer.call_count == 0)
            request = request_factory.post(flag_url)
            request.user = self.user
            request._dont_enforce_csrf_checks = True
            views.flag(request, 1)
            self.assertTrue(self.mailer.call_count == 0)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_OPTIONS=app_model_options_mock,
    )
    def test_no_email_when_flagging_a_comment_sent_to_an_article(self):
        # The comment with pk=2 has been sent to an article,
        # and the Article model has no moderation registered in
        # (test/models.py), so flagging the comment for removal
        # will not trigger the notify_removal_suggestion.
        flag_url = reverse("comments-flag", args=[2])
        self.assertTrue(self.mailer.call_count == 0)
        request = request_factory.post(flag_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        views.flag(request, 2)
        self.assertTrue(self.mailer.call_count == 0)

    def test_no_email_when_flag_is_other_than_suggest_removal(self):
        # Here the view is django_comments.views.delete, which
        # flags a comment with MODERATION_DELETION. So no email
        # is sent as notify_removal_suggestion requires that the flag
        # is REMOVAL_SUGGESTION.
        delete_url = reverse("comments-delete", args=[1])
        self.assertTrue(self.mailer.call_count == 0)
        # The user sending MODERATION_DELETION requires permission:
        # django_comments.can_moderate.
        ct_comments = ContentType.objects.get_for_model(Comment)
        can_moderate = Permission.objects.get(
            codename="can_moderate", content_type=ct_comments
        )
        self.user.user_permissions.add(can_moderate)
        # The rest is as in previous test methods.
        request = request_factory.post(delete_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        delete(request, 1)
        self.assertTrue(self.mailer.call_count == 0)
