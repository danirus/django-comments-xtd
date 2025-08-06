import json
from datetime import datetime
from unittest.mock import patch

import django_comments
import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.test import APIRequestFactory

from django_comments_xtd import get_model
from django_comments_xtd.api import views as api_views
from django_comments_xtd.conf import settings
from django_comments_xtd.models import TmpXtdComment
from django_comments_xtd.tests.models import Article
from django_comments_xtd.tests.utils import post_comment

app_model_options_mock = {"tests.article": {"who_can_post": "users"}}

XtdComment = get_model()

factory = APIRequestFactory()


class CommentCreateTestCase(TestCase):
    def setUp(self):
        patcher = patch("django_comments_xtd.views.send_mail")
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_CONFIRM_EMAIL=False
    )
    def test_post_returns_201_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.rendered_content)
        self.assertTrue("id" in data)
        self.assertEqual(data["id"], 1)  # id of the new created comment.

    def test_post_returns_2xx_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.mock_mailer.call_count, 1)

    def test_post_returns_4xx_response(self):
        # It uses an authenticated user, but the user has no mail address.
        self.user = User.objects.create_user("bob", "", "pwd")
        data = {
            "name": "",
            "email": "",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data, auth_user=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("name" in response.data)
        self.assertTrue("email" in response.data)
        self.assertEqual(self.mock_mailer.call_count, 0)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_OPTIONS=app_model_options_mock,
    )
    def test_post_returns_unauthorized_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.rendered_content, b'"User not authenticated"')
        self.assertEqual(self.mock_mailer.call_count, 0)

    def post_parent_comment(self):
        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site1 = Site.objects.get(pk=1)
        self.cm = XtdComment.objects.create(
            content_type=article_ct,
            object_pk=self.article.id,
            content_object=self.article,
            site=site1,
            comment="just a testing comment",
            submit_date=datetime.now(),
        )

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_MAX_THREAD_LEVEL=0,
        COMMENTS_XTD_CONFIRM_EMAIL=False,
    )
    def test_post_reply_to_exceeds_max_thread_level_returns_400_code(self):
        self.assertEqual(settings.COMMENTS_XTD_MAX_THREAD_LEVEL, 0)
        self.assertEqual(XtdComment.objects.count(), 0)
        self.post_parent_comment()
        self.assertEqual(XtdComment.objects.count(), 1)
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": self.cm.id,  # This exceeds max thread level.
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(XtdComment.objects.count(), 1)  # Comment not added.
        self.assertEqual(response.status_code, 400)


@pytest.mark.django_db
def test_PreviewUserAvatar_returns_avatar_url():
    req_data = {"email": "joe.bloggs@example.com"}
    request = factory.post(reverse("comments-xtd-api-preview"), req_data)
    view = api_views.PreviewUserAvatar.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    resp_data = json.loads(response.rendered_content)
    temp_comment = TmpXtdComment(
        {"user": None, "user_email": "joe.bloggs@example.com"}
    )
    get_user_avatar = import_string(settings.COMMENTS_XTD_API_GET_USER_AVATAR)
    assert resp_data["url"] == get_user_avatar(temp_comment)
