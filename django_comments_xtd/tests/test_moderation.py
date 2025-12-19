# ruff:noqa: N802
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import django_comments
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django_comments.models import Comment, CommentFlag
from django_comments.views.moderation import delete

from django_comments_xtd.models import XtdComment
from django_comments_xtd.templating import get_template_list
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
from django_comments_xtd.views import FlagCommentView

request_factory = RequestFactory()

send_mail = "django_comments.moderation.send_mail"


class ModeratorApprovesComment(TestCase):
    def setUp(self):
        self.patcher_app1 = patch(send_mail)
        self.patcher_app2 = patch("django_comments_xtd.views.utils.send_mail")
        self.mailer_app1 = self.patcher_app1.start()
        self.mailer_app2 = self.patcher_app2.start()
        self.diary_entry = Diary.objects.create(
            body="What I did on October...",
            allow_comments=True,
            publish=datetime.now(),
        )
        self.form = django_comments.get_form()(self.diary_entry)

    def tearDown(self):
        self.patcher_app1.stop()
        self.patcher_app2.stop()

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
        comment = django_comments.get_model().objects.for_model(Diary).first()
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
        comment = django_comments.get_model().objects.for_model(Diary).first()
        self.assertTrue(comment.is_public is True)


class ModeratorHoldsComment(TestCase):
    def setUp(self):
        self.patcher_app1 = patch(send_mail)
        self.patcher_app2 = patch("django_comments_xtd.views.utils.send_mail")
        self.mailer_app1 = self.patcher_app1.start()
        self.mailer_app2 = self.patcher_app2.start()
        self.diary_entry = Diary.objects.create(
            body="What I did Yesterday...",
            allow_comments=True,
            publish=datetime.now() - timedelta(days=5),
        )
        self.form = django_comments.get_form()(self.diary_entry)

    def tearDown(self):
        self.patcher_app1.stop()
        self.patcher_app2.stop()

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
        comment = django_comments.get_model().objects.for_model(Diary).first()
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
        comment = django_comments.get_model().objects.for_model(Diary).first()
        self.assertTrue(comment.is_public is False)

    def test_moderation_with_unregistered_user__template_moderated(self):
        # Same case as the previous. Only, it passes a kwargs
        # `template_moderated` to test that `views.confirm`
        # uses that parameter when given.
        self.post_valid_data()
        self.assertTrue(self.mailer_app1.call_count == 0)
        self.assertTrue(self.mailer_app2.call_count == 1)
        mail_msg = self.mailer_app2.call_args[0][1]
        key = str(
            re.search(r"http://.+/confirm/(?P<key>[\S]+)/", mail_msg).group(
                "key"
            )
        )
        template_list = get_template_list(
            "moderated", app_label="tests", model="diary"
        )
        confirm_comment_url(key, template_moderated=template_list)
        self.assertTrue(self.mailer_app1.call_count == 1)
        self.assertTrue(self.mailer_app2.call_count == 1)
        comment = django_comments.get_model().objects.for_model(Diary).first()
        self.assertTrue(comment.is_public is False)


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
        comment = django_comments.get_model().objects.for_model(Diary).first()
        flag_url = reverse("comments-flag", args=[comment.id])
        request = request_factory.get(flag_url)
        request.user = AnonymousUser()
        response = FlagCommentView.as_view()(request, comment.id)
        dest_url = "/accounts/login/?next=/comments/flag/1/"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, dest_url)

    def test_loggedin_user_can_flag_comment(self):
        comment = django_comments.get_model().objects.for_model(Diary).first()
        flag_url = reverse("comments-flag", args=[comment.id])
        request = request_factory.get(flag_url)
        request.user = self.user
        response = FlagCommentView.as_view()(request, comment.id)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find(b"Flag comment") > -1)
        request = request_factory.post(flag_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = FlagCommentView.as_view()(request, comment.id)
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
        FlagCommentView.as_view()(request, 1)
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
            FlagCommentView.as_view()(request, 1)
            self.assertTrue(self.mailer.call_count == 0)

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
        FlagCommentView.as_view()(request, 2)
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
