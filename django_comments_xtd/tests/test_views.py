import random
import re
import string
from datetime import datetime
from unittest.mock import patch

import django_comments
import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.urls import reverse

from django_comments_xtd import signals, signed, views
from django_comments_xtd.conf import settings
from django_comments_xtd.models import TmpXtdComment, XtdComment
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
    return views.PostCommentView.as_view()(request)


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
    return views.PostCommentView.as_view()(request)


def confirm_comment_url(key, follow=True, **extra_kwargs):
    request = request_factory.get(
        reverse("comments-xtd-confirm", kwargs={"key": key}), follow=follow
    )
    request.user = AnonymousUser()
    return views.confirm(request, key, **extra_kwargs)


app_model_config_mock = {"tests.article": {"who_can_post": "users"}}


# ----------------------------------------------------------------------
# @pytest.mark.django_db
# def test__send_email_confirmation_request(an_articles_comment, monkeypatch):
#     mock_send_mail = Mock()
#     monkeypatch.setattr(views.utils, "send_mail", mock_send_mail)
#     key = signed.dumps(
#         an_articles_comment,
#         compress=True,
#         extra_key=settings.COMMENTS_XTD_SALT,
#     )
#     site = Site.objects.get(pk=1)
#     views.send_email_confirmation_request(an_articles_comment, key, site)
#     subj, text_msg, from_mail, to_mail_lst = mock_send_mail.call_args[0]

#     assert subj == "comment confirmation request"
#     expected_confirmation_url = reverse(
#         "comments-xtd-confirm", args=[key.decode("utf-8")]
#     )
#     msg_ctx = {
#         "comment": an_articles_comment,
#         "confirmation_url": expected_confirmation_url,
#         "contact": settings.COMMENTS_XTD_CONTACT_EMAIL,
#         "site": site,
#     }
#     text_template = "comments/email_confirmation_request.txt"
#     text_msg_tmpl = loader.get_template(text_template)
#     expected_text_msg = text_msg_tmpl.render(msg_ctx)
#     assert text_msg == expected_text_msg
#     assert from_mail == settings.COMMENTS_XTD_FROM_EMAIL
#     assert to_mail_lst == ["alice@example.org"]


# @pytest.mark.django_db
# @patch.multiple(
#     "views.settings",
#     COMMENTS_XTD_SEND_HTML_EMAIL=True,
#     COMMENTS_XTD_SALT=b"Salt to enrich the signature",
# )
# def test__send_email_confirmation_request__html(
#     an_articles_comment, monkeypatch
# ):
#     mock_send_mail = Mock()
#     monkeypatch.setattr(views.utils, "send_mail", mock_send_mail)
#     key = signed.dumps(
#         an_articles_comment,
#         compress=True,
#         extra_key=settings.COMMENTS_XTD_SALT,
#     )
#     site = Site.objects.get(pk=1)
#     views.send_email_confirmation_request(an_articles_comment, key, site)

#     call_args, call_kwargs = mock_send_mail.call_args
#     subj, text_msg, from_mail, to_mail_lst = call_args
#     assert subj == "comment confirmation request"
#     expected_confirmation_url = reverse(
#         "comments-xtd-confirm", args=[key.decode("utf-8")]
#     )
#     msg_ctx = {
#         "comment": an_articles_comment,
#         "confirmation_url": expected_confirmation_url,
#         "contact": settings.COMMENTS_XTD_CONTACT_EMAIL,
#         "site": site,
#     }
#     text_template = "comments/email_confirmation_request.txt"
#     text_msg_tmpl = loader.get_template(text_template)
#     expected_text_msg = text_msg_tmpl.render(msg_ctx)
#     assert text_msg == expected_text_msg
#     assert from_mail == settings.COMMENTS_XTD_FROM_EMAIL
#     assert to_mail_lst == ["alice@example.org"]

#     html_template = "comments/email_confirmation_request.html"
#     html_msg_tmpl = loader.get_template(html_template)
#     expected_html_msg = html_msg_tmpl.render(msg_ctx)
#     assert call_kwargs["html"] == expected_html_msg


# ----------------------------------------------------------------------
@pytest.mark.django_db
def test__get_comment_if_exists(an_articles_comment):
    tmp_xtd_cm_1 = TmpXtdComment(
        user_name=an_articles_comment.user_name,
        user_email=an_articles_comment.user_email,
        followup=an_articles_comment.followup,
        submit_date=an_articles_comment.submit_date,
    )
    assert views.get_comment_if_exists(tmp_xtd_cm_1) == an_articles_comment

    tmp_xtd_cm_2 = TmpXtdComment(  # No XtdComment exists with these values.
        user_name="Does not exist",
        user_email="anonymous@example.org",
        followup=True,
        submit_date=an_articles_comment.submit_date,
    )
    assert views.get_comment_if_exists(tmp_xtd_cm_2) is None


# ----------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_object_str, expected_ctype_str, for_concrete_model",
    [
        ("a_diary_entry", "tests.diary", True),
        ("a_diary_with_mtl1", "tests.diary", True),
        ("a_diary_entry", "tests.diary", False),
        ("a_diary_with_mtl1", "tests.diarywithmtl1", False),
    ],
)
def test__create_comment__with_proxy_model(
    content_object_str, expected_ctype_str, for_concrete_model, request
):
    # When `COMMENTS_XTD_FOR_CONCRETE_MODEL` is `True`, sending a comment
    # to an object of a model that is marked as a Proxy model will record
    # the `content_type` as the parent of the Proxy model. This is the
    # expected behaviour. But if we want to alter the Proxy model to, ie:
    # have a higher max_thread_level, so that comments sent to that model
    # can be threaded differently as comments sent to the parent, then
    # we would turn `COMMENTS_XTD_FOR_CONCRETE_MODEL` to `False`, and the
    # `content_type` stored will be the Proxy model and not the parent.
    with patch.multiple(
        views.settings, COMMENTS_XTD_FOR_CONCRETE_MODEL=for_concrete_model
    ):
        obj = request.getfixturevalue(content_object_str)
        ctype = ContentType.objects.get_for_model(
            obj, for_concrete_model=for_concrete_model
        )
        tmp_comment = {
            "object_pk": obj.pk,
            "user_name": "Bob",
            "user_email": "bob@example.com",
            "user_url": "",
            "comment": "Es war einmal iene kleine...",
            "submit_date": datetime.now(),
            "site_id": 1,
            "is_public": True,
            "is_removed": False,
            "level": 0,
            "order": 1,
            "parent_id": 0,
            "followup": True,
            "ip_address": "127.0.0.1",
            "content_type": ctype,
            "content_object": obj,
        }
        comment = views.create_comment(tmp_comment)
    assert comment.content_type == ctype
    app, model = expected_ctype_str.split(".")
    expected_ctype = ContentType.objects.get(app_label=app, model=model)
    assert ctype == expected_ctype


# ----------------------------------------------------------------------
class OnCommentWasPostedTestCase(TestCase):
    def setUp(self):
        self.patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = self.patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)
        self.user = AnonymousUser()

    def tearDown(self):
        self.patcher.stop()

    def post_valid_data(self, auth_user=None, response_code=302):
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, self.article, auth_user)
        self.assertEqual(response.status_code, response_code)
        if response.status_code == 302:
            self.assertTrue(response.url.startswith("/comments/sent/?c="))

    def post_invalid_data(
        self, auth_user=None, response_code=302, remove_fields: list[str] = ()
    ):
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        if len(remove_fields):
            for field_name in remove_fields:
                data.pop(field_name)
        response = post_article_comment(data, self.article, auth_user)
        self.assertEqual(response.status_code, response_code)
        if response.status_code == 302:
            self.assertTrue(response.url.startswith("/comments/sent/?c="))

    def test_post_as_authenticated_user(self):
        self.user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data(auth_user=self.user)
        # no confirmation email sent as user is authenticated
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_post_as_authenticated_user_without_name_nor_email(self):
        self.user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_invalid_data(
            auth_user=self.user, remove_fields=["name", "email"]
        )
        # no confirmation email sent as user is authenticated via self.user.
        self.assertTrue(self.mock_mailer.call_count == 0)

    def test_confirmation_email_is_sent(self):
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data()
        self.assertTrue(self.mock_mailer.call_count == 1)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_CONFIG=app_model_config_mock,
    )
    def test_post_as_visitor_when_only_users_can_post(self):
        self.assertTrue(self.mock_mailer.call_count == 0)
        self.post_valid_data(response_code=400)
        self.assertTrue(self.mock_mailer.call_count == 0)


# ----------------------------------------------------------------------
class ConfirmCommentTestCase(TestCase):
    def setUp(self):
        patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = patcher.start()
        # Create random string so that it's harder for zlib to compress
        content = "".join(random.choice(string.printable) for _ in range(6096))
        self.article = Article.objects.create(
            title="September",
            slug="september",
            body="In September..." + content,
        )
        self.form = django_comments.get_form()(self.article)
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal iene kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        self.assertTrue(self.mock_mailer.call_count == 0)
        post_article_comment(data, self.article)
        self.assertTrue(self.mock_mailer.call_count == 1)
        self.key = str(
            re.search(
                r"http://.+/confirm/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        self.addCleanup(patcher.stop)

    def test_confirm_url_is_short_enough(self):
        # Tests that the length of the confirm url's length isn't
        # dependent on the article length.
        length = len(reverse("comments-xtd-confirm", kwargs={"key": self.key}))
        self.assertLessEqual(length, 4096, "Urls can only be a max of 4096")

    def test_400_on_bad_signature(self):
        response = confirm_comment_url(self.key[:-1])
        self.assertEqual(response.status_code, 400)

    def test_consecutive_confirmation_url_visits_works(self):
        # test that consecutives visits to the same confirmation URL produce
        # an Http 404 code, as the comment has already been verified in the
        # first visit
        resp1 = confirm_comment_url(self.key)
        self.assertEqual(resp1.status_code, 302)
        resp2 = confirm_comment_url(self.key, follow=False)
        self.assertEqual(resp2.status_code, resp1.status_code)

    def test_signal_receiver_may_discard_the_comment(self):
        # test that receivers of signal confirmation_received may return False
        # and thus rendering a template_discarded output
        def on_signal(sender, comment, request, **kwargs):
            return False

        self.assertEqual(self.mock_mailer.call_count, 1)  # sent during setUp
        signals.confirmation_received.connect(on_signal)
        response = confirm_comment_url(self.key)
        # mailing avoided by on_signal:
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.assertTrue(response.content.find(b"Comment discarded") > -1)

    def test_comment_is_created_and_view_redirect(self):
        # testing that visiting a correct confirmation URL creates a XtdComment
        # and redirects to the article detail page
        Site.objects.get_current().domain = "testserver"  # django bug #7743
        response = confirm_comment_url(self.key, follow=False)
        data = signed.loads(self.key, extra_key=settings.COMMENTS_XTD_SALT)
        try:
            comment = XtdComment.objects.get(
                content_type=data["content_type"],
                user_name=data["user_name"],
                user_email=data["user_email"],
                submit_date=data["submit_date"],
            )
        except XtdComment.DoesNotExist:
            comment = None
        self.assertTrue(comment is not None)
        self.assertEqual(response.url, comment.get_absolute_url())

    def test_notify_comment_followers(self):
        # send a couple of comments to the article with followup=True and check
        # that when the second comment is confirmed a followup notification
        # email is sent to the user who sent the first comment
        self.assertEqual(self.mock_mailer.call_count, 1)
        confirm_comment_url(self.key)
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send 2nd comment
        self.form = django_comments.get_form()(self.article)
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, article=self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(
            r"http://.+/confirm/(?P<key>[\S]+)/",
            self.mock_mailer.call_args[0][1],
        ).group("key")
        confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.assertTrue(
            # We can find the 'comment' in the text_message.
            self.mock_mailer.call_args[0][1].index(data["comment"]) > -1
        )
        articles_title = f"Post: {self.article.title}"
        self.assertTrue(
            # We can find article's title (comment.content_object.title).
            self.mock_mailer.call_args[0][1].index(articles_title) > -1
        )
        self.assertTrue(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assertTrue(
            self.mock_mailer.call_args[0][1].find(
                "There is a new comment following up yours."
            )
            > -1
        )

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_SEND_HTML_EMAIL=False
    )
    def test_notify_comment_followers_with_SEND_HTML_EMAIL_eq_False(self):
        # send a couple of comments to the article with followup=True and check
        # that when the second comment is confirmed a followup notification
        # email is sent to the user who sent the first comment
        self.assertEqual(self.mock_mailer.call_count, 1)
        confirm_comment_url(self.key)
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send 2nd comment
        self.form = django_comments.get_form()(self.article)
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, article=self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(
            r"http://.+/confirm/(?P<key>[\S]+)/",
            self.mock_mailer.call_args[0][1],
        ).group("key")
        confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.assertTrue(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assertTrue(
            self.mock_mailer.call_args[0][1].find(
                "There is a new comment following up yours."
            )
            > -1
        )
        self.assertEqual(self.mock_mailer.call_args[1], {"html": None})

    def test_notify_followers_dupes(self):
        # first of all confirm Bob's comment otherwise it doesn't reach DB
        confirm_comment_url(self.key)
        # then put in play pull-request-15's assert...
        # https://github.com/danirus/django-comments-xtd/pull/15
        diary = Diary.objects.create(body="Lorem ipsum", allow_comments=True)
        self.assertEqual(diary.pk, self.article.pk)

        self.form = django_comments.get_form()(diary)
        data = {
            "name": "Charlie",
            "email": "charlie@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_diary_comment(data, diary_entry=diary)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.key = str(
            re.search(
                r"http://.+/confirm/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        # 1) confirmation for Bob (sent in `setUp()`)
        # 2) confirmation for Charlie
        self.assertEqual(self.mock_mailer.call_count, 2)
        response = confirm_comment_url(self.key)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/cr/"))
        self.assertEqual(self.mock_mailer.call_count, 2)

        self.form = django_comments.get_form()(self.article)
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal iene kleine...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, article=self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.key = re.search(
            r"http://.+/confirm/(?P<key>[\S]+)/",
            self.mock_mailer.call_args[0][1],
        ).group("key")
        confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 4)
        self.assertTrue(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assertTrue(
            self.mock_mailer.call_args[0][1].find(
                "There is a new comment following up yours."
            )
            > -1
        )

    def test_no_notification_for_same_user_email(self):
        # test that a follow-up user_email don't get a notification when
        # sending another email to the thread
        self.assertEqual(self.mock_mailer.call_count, 1)
        confirm_comment_url(self.key)  # confirm Bob's comment
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send Bob's 2nd comment
        self.form = django_comments.get_form()(self.article)
        data = {
            "name": "Alice",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Bob's comment he shouldn't get notified about",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        post_article_comment(data, self.article)
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(
            r"http://.+/confirm/(?P<key>[\S]+)/",
            self.mock_mailer.call_args[0][1],
        ).group("key")
        confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 2)


class ReplyNoCommentTestCase(TestCase):
    def test_reply_non_existing_comment_raises_404(self):
        response = self.client.get(reverse("comments-xtd-reply", args=(1,)))
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

    def test_reply_view(self):
        response = self.client.get(reverse("comments-xtd-reply", args=(3,)))
        self.assertEqual(response.status_code, 200)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL=2,
    )
    def test_not_allow_threaded_reply_raises_403(self):
        response = self.client.get(reverse("comments-xtd-reply", args=(3,)))
        self.assertEqual(response.status_code, 403)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_CONFIG=app_model_config_mock,
    )
    def test_reply_as_visitor_when_only_users_can_post(self):
        response = self.client.get(reverse("comments-xtd-reply", args=(1,)))
        self.assertEqual(response.status_code, 302)  # Redirect to login.
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))


class MuteFollowUpTestCase(TestCase):
    def setUp(self):
        # Creates an article and send two comments to the article with
        # follow-up notifications. First comment doesn't have to send any
        #  notification.
        # Second comment has to send one notification (to Bob).
        patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="September", slug="september", body="John's September"
        )
        self.form = django_comments.get_form()(self.article)

        # Bob sends 1st comment to the article with follow-up
        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Nice September you had...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertTrue(self.mock_mailer.call_count == 1)
        bobkey = str(
            re.search(
                r"http://.+/confirm/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        confirm_comment_url(bobkey)  # confirm Bob's comment

        # Alice sends 2nd comment to the article with follow-up
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "followup": True,
            "reply_to": 1,
            "level": 1,
            "order": 1,
            "comment": "Yeah, great photos",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertTrue(self.mock_mailer.call_count == 2)
        alicekey = str(
            re.search(
                r"http://.+/confirm/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        confirm_comment_url(alicekey)  # confirm Alice's comment

        # Bob receives a follow-up notification
        self.assertTrue(self.mock_mailer.call_count == 3)
        self.bobs_mutekey = str(
            re.search(
                r"http://.+/mute/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        self.addCleanup(patcher.stop)

    def get_mute_followup_url(self, key):
        request = request_factory.get(
            reverse("comments-xtd-mute", kwargs={"key": key}), follow=True
        )
        request.user = AnonymousUser()
        response = views.MuteCommentView.as_view()(request, key)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find(b"Comment thread muted") > -1)
        return response

    def test_mute_followup_notifications(self):
        # Bob's receive a notification and click on the mute link to
        # avoid additional comment messages on the same article.
        self.get_mute_followup_url(self.bobs_mutekey)
        # Alice sends 3rd comment to the article with follow-up
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "followup": True,
            "reply_to": 2,
            "level": 1,
            "order": 1,
            "comment": "And look at this and that...",
            "next": reverse("comments-xtd-sent"),
        }
        data.update(self.form.initial)
        response = post_article_comment(data, self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        # Alice confirms her comment...
        self.assertTrue(self.mock_mailer.call_count == 4)
        alicekey = str(
            re.search(
                r"http://.+/confirm/(?P<key>[\S]+)/",
                self.mock_mailer.call_args[0][1],
            ).group("key")
        )
        confirm_comment_url(alicekey)  # confirm Alice's comment.
        # Alice confirmed her comment, but this time Bob won't receive any
        # notification, neither do Alice being the sender.
        self.assertTrue(self.mock_mailer.call_count == 4)

    def test_mute_followup_notifications_with_wrong_key(self):
        # Bob's receive a notification and click on the mute link to
        # avoid additional comment messages on the same article.
        # But we use a wrong key (just remove a few bits from the tail).
        key = self.bobs_mutekey[:-2]
        request = request_factory.get(
            reverse("comments-xtd-mute", kwargs={"key": key}), follow=True
        )
        request.user = AnonymousUser()
        response = views.MuteCommentView.as_view()(request, key)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.content.find(b"Bad Request") > -1)

    def test_muting_twice_raise_http_404(self):
        # Mute one time.
        self.get_mute_followup_url(self.bobs_mutekey)
        # Mute a second time.
        request = request_factory.get(
            reverse("comments-xtd-mute", kwargs={"key": self.bobs_mutekey}),
            follow=True,
        )
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            views.MuteCommentView.as_view()(request, self.bobs_mutekey)


class HTMLDisabledMailTestCase(TestCase):
    def setUp(self):
        # Create an article and send a comment. Test method will chech headers
        # to see wheter messages has multiparts or not.
        patcher = patch("django_comments_xtd.views.utils.send_mail")
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
            "next": reverse("comments-xtd-sent"),
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
            self.assertTrue(response.url.startswith("/comments/sent/?c="))
            self.assertTrue(self.mock_mailer.call_count == 1)
            self.assertTrue(self.mock_mailer.call_args[1]["html"] is None)

    def test_mail_does_contain_html_part(self):
        response = post_article_comment(self.data, self.article)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/comments/sent/?c="))
        self.assertTrue(self.mock_mailer.call_count == 1)
        self.assertTrue(self.mock_mailer.call_args[1]["html"] is not None)


# ---------------------------------------------------------------------
# Test 'post' via accessing the exposed functionality, to
# later replace the implementation with class-based views.


def test_post_view_requires_method_to_be_POST(rf):
    # GET should not work.
    request = rf.get(reverse("comments-xtd-post"))
    request._dont_enforce_csrf_checks = True
    response = views.PostCommentView.as_view()(request)
    assert response.status_code == 405

    # PUT should not work.
    request = rf.put(reverse("comments-xtd-post"))
    request._dont_enforce_csrf_checks = True
    response = views.PostCommentView.as_view()(request)
    assert response.status_code == 405

    # PATCH should not work.
    request = rf.patch(reverse("comments-xtd-post"))
    request._dont_enforce_csrf_checks = True
    response = views.PostCommentView.as_view()(request)
    assert response.status_code == 405
