# ruff:noqa: PLR2004
from datetime import datetime
from unittest.mock import patch

import django_comments
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django_comments.models import CommentFlag
from django_comments.views import comments

from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    XtdComment,
)
from django_comments_xtd.tests.models import Article, Diary

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
    return comments.post_comment(request)


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
    return comments.post_comment(request)


app_model_options_mock = {"tests.article": {"who_can_post": "users"}}


class DummyViewTestCase(TestCase):
    def setUp(self):
        self.user = AnonymousUser()

    def test_dummy_view_response(self):
        response = self.client.get(
            reverse(
                "diary-detail", kwargs={"year": 2022, "month": 10, "day": 4}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Got it")


class CommentViewsTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.site = Site.objects.get(pk=1)
        self.article = Article.objects.create(
            title="September",
            slug="september",
            body="What I did on September...",
        )
        self.comment = XtdComment.objects.create(
            content_object=self.article,
            site=self.site,
            comment="comment 1 to article",
        )
        self.diary = Diary.objects.create(body="What I did on September...")
        self.diary_comment = XtdComment.objects.create(
            content_object=self.diary,
            site=self.site,
            comment="comment 1 to diary",
        )

    def test_like_view(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-like", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm your opinion")
        self.assertContains(response, "Do you like this comment?")
        self.assertContains(response, self.diary.get_absolute_url())
        self.assertContains(
            response, "Please, confirm your opinion about the comment."
        )
        self.assertEqual(response.context["comment"], self.diary_comment)

    def test_like_view_contains_user_url_if_available(self):
        self.diary_comment.user_url = "https://example.com/user/me/"
        self.diary_comment.save()
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-like", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you like this comment?")
        self.assertContains(response, "https://example.com/user/me/")

    def test_like_view_already_liked(self):
        CommentFlag.objects.create(
            comment=self.diary_comment,
            user=self.user,
            flag=LIKEDIT_FLAG,
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-like", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm your opinion")
        self.assertContains(
            response, "You liked this comment, do you want to change it?"
        )
        self.assertContains(response, self.diary.get_absolute_url())
        self.assertContains(
            response, "Please, confirm your opinion about the comment."
        )
        self.assertContains(
            response,
            'Click on the "withdraw" button if you want '
            "to withdraw your positive opinion on this comment.",
        )
        self.assertEqual(response.context["comment"], self.diary_comment)

    @patch("django_comments_xtd.views_v2.get_app_model_options")
    def test_like_view_with_feedback_disabled(self, mock_get_app_model_options):
        mock_get_app_model_options.return_value = {"allow_feedback": False}
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-like", args=[self.comment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_like_done_view(self):
        response = self.client.get(reverse("comments-xtd-like-done"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your opinion is appreciated")
        self.assertContains(
            response, "Thanks for taking the time to participate."
        )

    def test_dislike_view(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-dislike", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm your opinion")
        self.assertContains(response, "Do you dislike this comment?")
        self.assertContains(response, self.diary.get_absolute_url())
        self.assertContains(
            response, "Please, confirm your opinion about the comment."
        )
        self.assertEqual(response.context["comment"], self.diary_comment)

    def test_dislike_view_contains_user_url_if_available(self):
        self.diary_comment.user_url = "https://example.com/user/me/"
        self.diary_comment.save()
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-dislike", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you dislike this comment?")
        self.assertContains(response, "https://example.com/user/me/")

    def test_dislike_view_already_disliked(self):
        CommentFlag.objects.create(
            comment=self.diary_comment,
            user=self.user,
            flag=DISLIKEDIT_FLAG,
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-dislike", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm your opinion")
        self.assertContains(
            response, "You didn't like this comment, do you want to change it?"
        )
        self.assertContains(response, self.diary.get_absolute_url())
        self.assertContains(
            response, "Please, confirm your opinion about the comment."
        )
        self.assertContains(
            response,
            'Click on the "withdraw" button if you want '
            "to withdraw your negative opinion on this comment.",
        )
        self.assertEqual(response.context["comment"], self.diary_comment)

    @patch("django_comments_xtd.views_v2.get_app_model_options")
    def test_dislike_view_with_feedback_disabled(
        self, mock_get_app_model_options
    ):
        mock_get_app_model_options.return_value = {"allow_feedback": False}
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-dislike", args=[self.comment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_dislike_done_view(self):
        response = self.client.get(reverse("comments-xtd-dislike-done"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You disliked the comment")
        self.assertContains(
            response, "Thanks for taking the time to participate."
        )

    def test_flag_view(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-flag", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flag comment")
        self.assertContains(response, "Flag this comment?")
        self.assertContains(response, self.diary.get_absolute_url())
        self.assertContains(
            response,
            "Click on the flag button to mark the following comment "
            "as inappropriate.",
        )
        self.assertEqual(response.context["comment"], self.diary_comment)

    def test_flag_view_contains_user_url_if_available(self):
        self.diary_comment.user_url = "https://example.com/user/me/"
        self.diary_comment.save()
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-flag", args=[self.diary_comment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flag comment")
        self.assertContains(response, "https://example.com/user/me/")

    @patch("django_comments_xtd.views_v2.get_app_model_options")
    def test_flag_view_with_flagging_disabled(self, mock_get_app_model_options):
        mock_get_app_model_options.return_value = {"allow_flagging": False}
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-flag", args=[self.comment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_flag_done_view(self):
        response = self.client.get(
            reverse("comments-flag-done"), data={"c": self.comment.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comment flagged")
        self.assertContains(response, "The comment has been flagged.")
        self.assertContains(response, self.article.get_absolute_url())
        self.assertContains(
            response,
            "Thank you for taking the time to improve the quality "
            "of discussion in our site.",
        )
        self.assertEqual(response.context["comment"], self.comment)

    def test_delete_view(self):
        self.user.user_permissions.add(
            Permission.objects.get_by_natural_key(
                codename="can_moderate",
                app_label="django_comments",
                model="comment",
            )
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-delete", kwargs={"comment_id": self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove comment")
        self.assertContains(response, "Remove this comment?")
        self.assertContains(response, self.comment.get_absolute_url())
        self.assertContains(response, "As a moderator you can delete comments.")
        self.assertContains(
            response,
            "Deleting a comment does not remove it from the site, "
            "only prevents your website from showing the text.",
        )
        self.assertEqual(response.context["comment"], self.comment)

    def test_delete_view_contains_user_url_if_available(self):
        self.comment.user_url = "https://example.com/user/me/"
        self.comment.save()
        self.user.user_permissions.add(
            Permission.objects.get_by_natural_key(
                codename="can_moderate",
                app_label="django_comments",
                model="comment",
            )
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-delete", kwargs={"comment_id": self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove comment")
        self.assertContains(response, "https://example.com/user/me/")

    def test_delete_done_view(self):
        response = self.client.get(
            reverse("comments-delete-done"), data={"c": self.comment.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comment removed")
        self.assertContains(response, "The comment has been removed.")
        self.assertContains(response, self.article.get_absolute_url())
        self.assertContains(
            response,
            "Thank you for taking the time to improve the quality"
            " of discussion in our site.",
        )
        self.assertEqual(response.context["comment"], self.comment)

    def test_reply_form(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-reply", kwargs={"cid": self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comment reply")
        self.assertContains(response, "Reply to comment")
        self.assertContains(response, "Post your comment")
        self.assertEqual(response.context["comment"], self.comment)

    def test_reply_contains_user_url_if_available(self):
        self.comment.user_url = "https://example.com/user/me/"
        self.comment.save()
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("comments-xtd-reply", kwargs={"cid": self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comment reply")
        self.assertContains(response, "https://example.com/user/me/")


class XtdCommentListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.article_ct = ContentType.objects.get(
            app_label="tests", model="article"
        )
        self.site = Site.objects.get(pk=1)
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )

    def test_contains_comment(self):
        XtdComment.objects.create(
            content_object=self.article,
            site=self.site,
            comment="comment 1 to article",
            is_removed=False,
            is_public=True,
        )
        response = self.client.get(reverse("comments-xtd-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "comment 1 to article")

    def test_not_contains_removed_comments_or_marker(self):
        XtdComment.objects.create(
            content_object=self.article,
            site=self.site,
            comment="comment 1 to article",
            is_removed=True,
            is_public=True,
        )
        response = self.client.get(reverse("comments-xtd-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "comment 1 to article")
        self.assertNotContains(response, "This comment has been removed.")


class OnCommentWasPostedTestCase(TestCase):
    def setUp(self):
        patcher = patch("django_comments_xtd.views_v2.send_mail")
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)
        self.user = AnonymousUser()

    def post_valid_data(self, auth_user=None, response_code=302):
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
        response = post_article_comment(data, self.article, auth_user)
        self.assertEqual(response.status_code, response_code)
        if response.status_code == 302:
            self.assertTrue(response.url.startswith("/comments/posted/?c="))

    def test_post_as_authenticated_user(self):
        self.user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data(auth_user=self.user)
        # no confirmation email sent as user is authenticated
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_confirmation_email_is_sent(self):
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data()
        self.assertTrue(self.mock_mailer.call_count == 1)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_OPTIONS=app_model_options_mock,
    )
    def test_post_as_visitor_when_only_users_can_post(self):
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data(response_code=400)
        self.assertTrue(self.mock_mailer.call_count == 0)


class ReplyNoCommentTestCase(TestCase):
    def test_reply_non_existing_comment_raises_404(self):
        response = self.client.get(
            reverse("comments-xtd-reply", kwargs={"cid": 1})
        )
        self.assertContains(response, "404", status_code=404)


class ReplyCommentTestCase(TestCase):
    def setUp(self):
        article = Article.objects.create(
            title="September",
            slug="september",
            body="What I did on September...",
        )
        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site = Site.objects.get(pk=1)

        # post Comment 1 to article, level 0
        XtdComment.objects.create(
            content_type=article_ct,
            object_pk=article.id,
            content_object=article,
            site=site,
            comment="comment 1 to article",
            submit_date=datetime.now(),
        )

        # post Comment 2 to article, level 1
        XtdComment.objects.create(
            content_type=article_ct,
            object_pk=article.id,
            content_object=article,
            site=site,
            comment="comment 1 to comment 1",
            submit_date=datetime.now(),
            parent_id=1,
        )

        # post Comment 3 to article, level 2 (max according to test settings)
        XtdComment.objects.create(
            content_type=article_ct,
            object_pk=article.id,
            content_object=article,
            site=site,
            comment="comment 1 to comment 1",
            submit_date=datetime.now(),
            parent_id=2,
        )

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_MAX_THREAD_LEVEL=2
    )
    def test_not_allow_threaded_reply_raises_403(self):
        response = self.client.get(
            reverse("comments-xtd-reply", kwargs={"cid": 3})
        )
        self.assertEqual(response.status_code, 403)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_OPTIONS=app_model_options_mock,
    )
    def test_reply_as_visitor_when_only_users_can_post(self):
        response = self.client.get(
            reverse("comments-xtd-reply", kwargs={"cid": 1})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login.
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))


class HTMLDisabledMailTestCase(TestCase):
    def setUp(self):
        # Create an article and send a comment. Test method will check headers
        # to see whether messages have multiparts or not.
        patcher = patch("django_comments_xtd.views_v2.send_mail")
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="September", slug="september", body="John's September"
        )
        self.form = django_comments.get_form()(self.article)

        # Bob sends 1st comment to the article with follow-up
        self.data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Nice September you had...",
        }
        self.data.update(self.form.initial)

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_SEND_HTML_EMAIL=False
    )
    def test_mail_does_not_contain_html_part(self):
        with patch.multiple(
            "django_comments_xtd.conf.settings",
            COMMENTS_XTD_SEND_HTML_EMAIL=False,
        ):
            response = post_article_comment(self.data, self.article)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/comments/posted/?c="))
            self.assertTrue(self.mock_mailer.call_count == 1)
            self.assertTrue(self.mock_mailer.call_args[1]["html"] is None)

    def test_mail_does_contain_html_part(self):
        response = post_article_comment(self.data, self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/posted/?c="))
        self.assertTrue(self.mock_mailer.call_count == 1)
        self.assertTrue(self.mock_mailer.call_args[1]["html"] is not None)
