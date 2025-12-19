import json
from datetime import datetime
from unittest.mock import Mock, patch

import django_comments
import pytest
import pytz
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django_comments.moderation import CommentModerator
from django_comments.signals import comment_will_be_posted
from rest_framework.test import APIClient

from django_comments_xtd.api.serializers import (
    FlagSerializer,
    ReadCommentReactionAuthorSerializer,
    ReadCommentSerializer,
    WriteCommentReactionSerializer,
    WriteCommentSerializer,
)
from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment
from django_comments_xtd.moderation import moderator
from django_comments_xtd.signals import should_request_be_authorized
from django_comments_xtd.tests.models import (
    Article,
    Diary,
    Quote,
    authorize_api_post_comment,
    comment_will_be_rejected,
)
from django_comments_xtd.tests.test_models import add_comment_to_diary_entry
from django_comments_xtd.tests.utils import post_comment


class FakeRequest:
    def __init__(self, user):
        self.user = user
        self.auth = None


class WriteCommentSerializerAsVisitorTestCase(TestCase):
    def setUp(self):
        self.patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = self.patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)
        # Remove the following fields on purpose, as we don't know them and
        # therefore we don't send them when using the web API (unless when)
        # using the JavaScript plugin, but that is not the case being tested
        # here.
        for field_name in ["security_hash", "timestamp"]:
            self.form.initial.pop(field_name)

    def tearDown(self):
        self.patcher.stop()

    def test_post_comment_before_connecting_signal(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.rendered_content,
            b'{"detail":"You do not have permission to perform this action."}',
        )
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_post_comment_after_connecting_signal(self):
        should_request_be_authorized.connect(authorize_api_post_comment)
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        client = APIClient()
        token = "Token 08d9fd42468aebbb8087b604b526ff0821ce4525"
        client.credentials(HTTP_AUTHORIZATION=token)
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse("comments-xtd-api-create"), data)
        self.assertEqual(response.status_code, 204)  # Confirmation req sent.
        self.assertTrue(self.mock_mailer.call_count == 1)
        should_request_be_authorized.disconnect(authorize_api_post_comment)


# ----------------------------------------------------------------------
def add_comment_to_quote(quote):
    quote_ct = ContentType.objects.get(app_label="tests", model="quote")
    site = Site.objects.get(pk=1)
    XtdComment.objects.create(
        content_type=quote_ct,
        object_pk=quote.id,
        content_object=quote,
        site=site,
        comment="cmt to quote",
        submit_date=datetime.now(),
    )


class WriteCommentSerializerTestCase(TestCase):
    def setUp(self):
        self.patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = self.patcher.start()
        self.user = User.objects.create_user(
            "joe", "joe@bloggs.com", "pwd", first_name="Joe", last_name="Bloggs"
        )
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)
        # Remove the following fields on purpose, as we don't know them and
        # therefore we don't send them when using the web API (unless when)
        # using the JavaScript plugin, but that is not the case being tested
        # here.
        for field_name in ["security_hash", "timestamp"]:
            self.form.initial.pop(field_name)
        should_request_be_authorized.connect(authorize_api_post_comment)

    def tearDown(self):
        self.patcher.stop()
        should_request_be_authorized.disconnect(authorize_api_post_comment)

    def test_post_comment_as_registered_user_after_connecting_signal(self):
        data = {
            "name": "",
            "email": "",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should work",
        }
        data.update(self.form.initial)
        client = APIClient()
        client.login(username="joe", password="pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse("comments-xtd-api-create"), data)
        self.assertEqual(response.status_code, 201)  # Comment created.
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_post_comment_can_be_rejected(self):
        comment_will_be_posted.connect(comment_will_be_rejected)
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        client = APIClient()
        client.login(username="joe", password="pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse("comments-xtd-api-create"), data)
        self.assertEqual(response.status_code, 403)  # Comment created.
        self.assertTrue(self.mock_mailer.call_count == 0)
        comment_will_be_posted.disconnect(comment_will_be_rejected)

    def test_post_comment_can_be_put_in_moderation(self):  # code 202.
        # Set article's date back to 1990. And set up moderation for old
        # objects.
        self.article.publish = datetime(1990, 1, 1)
        self.article.save()

        # Create the moderator class, and register it so that comments
        # posted to Article are moderated using the class
        # PostCommentModerator.
        class PostCommentModerator(CommentModerator):
            email_notification = False
            auto_moderate_field = "publish"
            moderate_after = 365

        moderator.register(Article, PostCommentModerator)

        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        client = APIClient()
        client.login(username="joe", password="pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        response = client.post(reverse("comments-xtd-api-create"), data)
        self.assertEqual(response.status_code, 202)  # Comment created.
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_validate_name_without_value(self):
        data = {
            "name": "",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This is a comment",
        }
        data.update(self.form.initial)
        mock_user = Mock(spec=self.user, autospec=True)
        mock_user.configure_mock(
            **{
                "get_username.return_value": self.user.username,
                "is_authenticated": self.user.is_authenticated,
            }
        )
        delattr(mock_user, "get_full_name")
        req = FakeRequest(mock_user)
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.data["name"], self.user.username)

    def test_validate_name_fails(self):
        data = {
            "name": "",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This is a comment",
        }
        data.update(self.form.initial)
        mock_user = Mock(spec=self.user, autospec=True)
        mock_user.configure_mock(
            **{
                "get_username.return_value": self.user.username,
                "is_authenticated": self.user.is_authenticated,
            }
        )
        delattr(mock_user, "get_full_name")
        delattr(mock_user, "get_username")
        req = FakeRequest(mock_user)
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"name": ["This field is required"]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate_email_fails(self):
        data = {
            "name": "Joe Bloggs",
            "email": "",
            "followup": True,
            "reply_to": 0,
            "comment": "This is a comment",
        }
        data.update(self.form.initial)
        mock_user = Mock(spec=self.user, autospec=True)
        mock_user.configure_mock(
            is_authenticated=self.user.is_authenticated,
            email=None,
        )
        req = FakeRequest(mock_user)
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"email": ["This field is required"]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate_reply_to_does_not_exist(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 1,
            "comment": "This is a comment",
        }
        data.update(self.form.initial)
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"reply_to": ["reply_to comment does not exist"]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate__reply_to__raises__ValidationError(self):
        diary_entry = Diary.objects.create(body="About Today...")
        add_comment_to_diary_entry(diary_entry)
        cm = XtdComment.objects.first()
        data = {
            "name": "",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": cm.id,
            "comment": "This is a comment",
        }
        self.form = django_comments.get_form()(diary_entry)
        # Remove the following fields on purpose, as we don't know them and
        # therefore we don't send them when using the web API (unless when)
        # using the JavaScript plugin, but that is not the case being tested
        # here.
        for field_name in ["security_hash", "timestamp"]:
            self.form.initial.pop(field_name)
        data.update(self.form.initial)
        req = FakeRequest(self.user)
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"reply_to": ["Max thread level reached"]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_content_type_or_object_pk_cant_be_None(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        # Make content_type None.
        data.update(self.form.initial)
        data["content_type"] = None
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"content_type": ["This field may not be null."]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

        # Make object_pk None.
        data.update(self.form.initial)
        data["object_pk"] = None
        ser = WriteCommentSerializer(data=data, context={"request": None})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"object_pk": ["This field may not be null."]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate_forging_content_type_raises_LookupError(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        data["content_type"] = "doesnot.exist"
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = (
            '{"non_field_errors": ["Invalid content_type '
            "value: 'doesnot.exist'\"]}"
        )
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate_forging_content_type_raises_model_DoesNotExist(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        data["content_type"] = "auth.user"
        data["object_pk"] = "2"
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = (
            '{"non_field_errors": ["No object matching '
            "content-type 'auth.user' and object PK '2'.\"]}"
        )
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate_forging_object_pk_raises_ValueError(self):
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": 0,
            "comment": "This post comment request should fail",
        }
        data.update(self.form.initial)
        data["object_pk"] = "tal"
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = (
            '{"non_field_errors": ["Attempting to get '
            "content-type 'tests.article' and object "
            "PK 'tal' raised Field 'id' expected a number "
            "but got 'tal'.\"]}"
        )
        self.assertEqual(json.dumps(ser.errors), expected_errors)

    def test_validate__whocan__is__users(self):
        a_quote = Quote.objects.create(
            title="Bilbo Farewell",
            slug="bilbo-farewell",
            quote="I don't know half of you half as well as you...",
        )
        add_comment_to_quote(a_quote)
        cm = XtdComment.objects.first()
        data = {
            "name": "Joe Bloggs",
            "email": "joe@bloggs.com",
            "followup": True,
            "reply_to": cm.id,
            "comment": "This is a comment",
        }
        self.form = django_comments.get_form()(a_quote)
        # Remove the following fields on purpose, as we don't know them and
        # therefore we don't send them when using the web API (unless when)
        # using the JavaScript plugin, but that is not the case being tested
        # here.
        for field_name in ["security_hash", "timestamp"]:
            self.form.initial.pop(field_name)
        data.update(self.form.initial)
        req = FakeRequest(AnonymousUser())
        ser = WriteCommentSerializer(data=data, context={"request": req})
        self.assertFalse(ser.is_valid())
        expected_errors = '{"non_field_errors": ["User not authenticated"]}'
        self.assertEqual(json.dumps(ser.errors), expected_errors)


class RenderSubmitDateTestCase(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )

    def create_comment(self, submit_date_is_aware=True):
        site = Site.objects.get(pk=1)
        ctype = ContentType.objects.get(app_label="tests", model="article")
        if submit_date_is_aware:
            utc = pytz.timezone("UTC")
            submit_date = datetime(2021, 1, 10, 10, 15, tzinfo=utc)
        else:
            submit_date = datetime(2021, 1, 10, 10, 15)
        self.cm = XtdComment.objects.create(
            content_type=ctype,
            object_pk=self.article.id,
            content_object=self.article,
            site=site,
            name="Joe Bloggs",
            email="joe@bloggs.com",
            comment="Just a comment",
            submit_date=submit_date,
        )

    @patch.multiple("django.conf.settings", USE_TZ=False)
    @patch.multiple("django_comments_xtd.conf.settings", USE_TZ=False)
    def test_submit_date_when_use_tz_is_false(self):
        self.create_comment(submit_date_is_aware=False)
        qs = XtdComment.objects.all()
        ser = ReadCommentSerializer(qs, context={"request": None}, many=True)
        self.assertEqual(
            ser.data[0]["submit_date"], "Jan. 10, 2021, 10:15 a.m."
        )

    @patch.multiple("django.conf.settings", USE_TZ=True)
    @patch.multiple("django_comments_xtd.conf.settings", USE_TZ=True)
    def test_submit_date_when_use_tz_is_true(self):
        self.create_comment(submit_date_is_aware=True)
        qs = XtdComment.objects.all()
        ser = ReadCommentSerializer(qs, context={"request": None}, many=True)
        self.assertEqual(
            ser.data[0]["submit_date"], "Jan. 10, 2021, 11:15 a.m."
        )


# ---------------------------------------------------------------------
# Tests for FlagSerializer. Using pytest instead of unittest.


@pytest.mark.django_db
def test_flag_serializer_is_valid(an_articles_comment):
    data = {"comment": an_articles_comment.pk, "flag": "report"}
    ser = FlagSerializer(data=data)
    assert ser.is_valid()


@pytest.mark.django_db
def test_flag_serializer_is_not_valid(an_articles_comment):
    data = {"comment": an_articles_comment.pk, "flag": "non-supported-flag"}
    ser = FlagSerializer(data=data)
    assert not ser.is_valid()


@pytest.mark.django_db
def test_ReadReactionsField(a_comments_reaction, an_user):
    context = {"request": None}
    ser = ReadCommentSerializer(a_comments_reaction.comment, context=context)
    assert len(ser.data["reactions"]) == 1
    reaction = ser.data["reactions"][0]
    assert "reaction" in reaction and reaction["reaction"] == "+"
    assert "label" in reaction and reaction["label"] == "+1"
    assert "icon" in reaction and reaction["icon"] == "#128077"
    assert "authors" in reaction and len(reaction["authors"]) == 1
    author = reaction["authors"][0]
    assert author["id"] == an_user.id
    assert author["author"] == settings.COMMENTS_XTD_FN_USER_REPR(an_user)


@pytest.mark.django_db
def test_ReadCommentSerializer_get_flags(a_comments_flag):
    context = {"request": None}
    ser = ReadCommentSerializer(a_comments_flag.comment, context=context)
    assert len(ser.data["flags"]) == 1
    flag = ser.data["flags"][0]
    assert flag["flag"] == "removal"
    assert flag["id"] == a_comments_flag.user.id
    user_repr = settings.COMMENTS_XTD_FN_USER_REPR(a_comments_flag.user)
    assert flag["user"] == user_repr


@pytest.mark.django_db
def test_ReadCommentSerializer_get_comment__is_removed(
    an_articles_comment_removed
):
    context = {"request": None}
    ser = ReadCommentSerializer(an_articles_comment_removed, context=context)
    assert ser.data["is_removed"] is True
    assert ser.data["comment"] == "This comment has been removed."


@pytest.mark.django_db
def test_ReadCommentReactionAuthorSerializer(a_comments_reaction):
    context = {"request": None}
    first_reaction_author = a_comments_reaction.authors.first()
    ser = ReadCommentReactionAuthorSerializer(
        first_reaction_author, context=context
    )
    assert ser.data["id"] == first_reaction_author.id
    assert ser.data["author"] == first_reaction_author.username


@pytest.mark.django_db
def test_WriteCommentReactionSerializer(an_articles_comment):
    # 1st: Test a non-existing reaction is caught by the serializer.
    ser = WriteCommentReactionSerializer(
        data={"reaction": "?", "comment": an_articles_comment}
    )
    assert ser.is_valid() is False
    assert "reaction" in ser.errors
    assert ser.errors["reaction"][0].code == "invalid_choice"

    # 2nd: Test an existing reaction makes the serializer valid.
    ser = WriteCommentReactionSerializer(
        data={"reaction": "+", "comment": an_articles_comment}
    )
    assert ser.is_valid() is True
