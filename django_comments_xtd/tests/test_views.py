from __future__ import unicode_literals

import re
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from datetime import datetime

# from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
# from django.test.utils import override_settings

from django_comments_xtd import django_comments, signals, signed
from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article, Diary


class OnCommentWasPostedTestCase(TestCase):
    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.form = django_comments.get_form()(self.article)

    def post_valid_data(self, wait_mail=True):
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data, follow=True)

    def test_post_as_authenticated_user(self):
        User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        self.assert_(self.mock_mailer.call_count == 0)
        self.post_valid_data(wait_mail=False)
        # no confirmation email sent as user is authenticated
        self.assert_(self.mock_mailer.call_count == 0)

    def test_confirmation_email_is_sent(self):
        self.assert_(self.mock_mailer.call_count == 0)
        self.post_valid_data()
        self.assert_(self.mock_mailer.call_count == 1)
        self.assertTemplateUsed(self.response, "comments/posted.html")


class ConfirmCommentTestCase(TestCase):
    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(title="September",
                                              slug="september",
                                              body="What I did on September...")
        self.form = django_comments.get_form()(self.article)
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal iene kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data)
        self.assert_(self.mock_mailer.call_count == 1)
        self.key = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                                 self.mock_mailer.call_args[0][1]).group("key"))
        self.addCleanup(patcher.stop)

    def get_confirm_comment_url(self, key):
        self.response = self.client.get(reverse("comments-xtd-confirm",
                                                kwargs={'key': key}),
                                        follow=True)

    def test_404_on_bad_signature(self):
        self.get_confirm_comment_url(self.key[:-1])
        self.assertContains(self.response, "404", status_code=404)

    def test_consecutive_confirmation_url_visits_fail(self):
        # test that consecutives visits to the same confirmation URL produce
        # an Http 404 code, as the comment has already been verified in the
        # first visit
        self.get_confirm_comment_url(self.key)
        self.get_confirm_comment_url(self.key)
        self.assertContains(self.response, "404", status_code=404)

    def test_signal_receiver_may_discard_the_comment(self):
        # test that receivers of signal confirmation_received may return False
        # and thus rendering a template_discarded output
        def on_signal(sender, comment, request, **kwargs):
            return False

        self.assertEqual(self.mock_mailer.call_count, 1)  # sent during setUp
        signals.confirmation_received.connect(on_signal)
        self.get_confirm_comment_url(self.key)
        # mailing avoided by on_signal:
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.assertTemplateUsed(self.response,
                                "django_comments_xtd/discarded.html")

    def test_comment_is_created_and_view_redirect(self):
        # testing that visiting a correct confirmation URL creates a XtdComment
        # and redirects to the article detail page
        Site.objects.get_current().domain = "testserver"  # django bug #7743
        self.get_confirm_comment_url(self.key)
        data = signed.loads(self.key, extra_key=settings.COMMENTS_XTD_SALT)
        try:
            comment = XtdComment.objects.get(
                content_type=data["content_type"],
                user_name=data["user_name"],
                user_email=data["user_email"],
                submit_date=data["submit_date"])
        except:
            comment = None
        self.assert_(comment is not None)
        redirected_to = 'http://testserver%s' % self.article.get_absolute_url()
        self.assertRedirects(self.response, redirected_to)

    def test_notify_comment_followers(self):
        # send a couple of comments to the article with followup=True and check
        # that when the second comment is confirmed a followup notification
        # email is sent to the user who sent the first comment
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.get_confirm_comment_url(self.key)
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send 2nd comment
        self.form = django_comments.get_form()(self.article)
        data = {"name": "Alice", "email": "alice@example.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data)
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                             self.mock_mailer.call_args[0][1]).group("key")
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.assert_(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assert_(self.mock_mailer.call_args[0][1].find(
            "There is a new comment following up yours.") > -1)

    def test_notify_followers_dupes(self):
        # first of all confirm Bob's comment otherwise it doesn't reach DB
        self.get_confirm_comment_url(self.key)
        # then put in play pull-request-15's assert...
        # https://github.com/danirus/django-comments-xtd/pull/15
        diary = Diary.objects.create(
            body='Lorem ipsum',
            allow_comments=True
        )
        self.assertEqual(diary.pk, self.article.pk)

        self.form = django_comments.get_form()(diary)
        data = {"name": "Charlie", "email": "charlie@example.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..."}
        data.update(self.form.initial)

        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data)
        self.key = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                                 self.mock_mailer.call_args[0][1]).group("key"))
        # 1) confirmation for Bob (sent in `setUp()`)
        # 2) confirmation for Charlie
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 2)

        self.form = django_comments.get_form()(self.article)
        data = {"name": "Alice", "email": "alice@example.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal iene kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.key = re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                             self.mock_mailer.call_args[0][1]).group("key")
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 4)
        self.assert_(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assert_(self.mock_mailer.call_args[0][1].find(
            "There is a new comment following up yours.") > -1)

    def test_no_notification_for_same_user_email(self):
        # test that a follow-up user_email don't get a notification when
        # sending another email to the thread
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.get_confirm_comment_url(self.key)  # confirm Bob's comment
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send Bob's 2nd comment
        self.form = django_comments.get_form()(self.article)
        data = {"name": "Alice", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Bob's comment he shouldn't get notified about"}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"),
                                         data=data)
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                             self.mock_mailer.call_args[0][1]).group("key")
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 2)


class ReplyNoCommentTestCase(TestCase):
    def test_reply_non_existing_comment_raises_404(self):
        response = self.client.get(reverse("comments-xtd-reply",
                                           kwargs={"cid": 1}))
        self.assertContains(response, "404", status_code=404)


class ReplyCommentTestCase(TestCase):
    def setUp(self):
        article = Article.objects.create(title="September",
                                         slug="september",
                                         body="What I did on September...")
        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site = Site.objects.get(pk=1)

        # post Comment 1 to article, level 0
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=article.id,
                                  content_object=article,
                                  site=site,
                                  comment="comment 1 to article",
                                  submit_date=datetime.now())

        # post Comment 2 to article, level 1
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=article.id,
                                  content_object=article,
                                  site=site,
                                  comment="comment 1 to comment 1",
                                  submit_date=datetime.now(),
                                  parent_id=1)

        # post Comment 3 to article, level 2 (max according to test settings)
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=article.id,
                                  content_object=article,
                                  site=site,
                                  comment="comment 1 to comment 1",
                                  submit_date=datetime.now(),
                                  parent_id=2)

    def test_reply_renders_max_thread_level_template(self):
        response = self.client.get(reverse("comments-xtd-reply",
                                           kwargs={"cid": 3}))
        self.assertTemplateUsed(response,
                                "django_comments_xtd/max_thread_level.html")


class MuteFollowUpsTestCase(TestCase):

    def setUp(self):
        # Creates an article and send two comments to the article with follow-up
        # notifications. First comment doesn't have to send any notification.
        # Second comment has to send one notification (to Bob).
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="September", slug="september", body="John's September")
        self.form = django_comments.get_form()(self.article)

        # Bob sends 1st comment to the article with follow-up
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Nice September you had..."}
        data.update(self.form.initial)
        self.client.post(reverse("comments-post-comment"), data=data)
        self.assert_(self.mock_mailer.call_count == 1)
        bobkey = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                               self.mock_mailer.call_args[0][1]).group("key"))
        self.get_confirm_comment_url(bobkey)  # confirm Bob's comment

        # Alice sends 2nd comment to the article with follow-up
        data = {"name": "Alice", "email": "alice@example.com",
                "followup": True, "reply_to": 1, "level": 1, "order": 1,
                "comment": "Yeah, great photos"}
        data.update(self.form.initial)
        self.client.post(reverse("comments-post-comment"), data=data)
        self.assert_(self.mock_mailer.call_count == 2)
        alicekey = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                                 self.mock_mailer.call_args[0][1]).group("key"))
        self.get_confirm_comment_url(alicekey)  # confirm Alice's comment

        # Bob receives a follow-up notification
        self.assert_(self.mock_mailer.call_count == 3)
        self.bobs_mutekey = str(re.search(
            r'http://.+/mute/(?P<key>[\S]+)',
            self.mock_mailer.call_args[0][1]).group("key"))
        self.addCleanup(patcher.stop)

    def get_confirm_comment_url(self, key):
        self.response = self.client.get(reverse("comments-xtd-confirm",
                                                kwargs={'key': key}),
                                        follow=True)

    def get_mute_followup_url(self, key):
        self.response = self.client.get(reverse("comments-xtd-mute",
                                                kwargs={'key': key}),
                                        follow=True)

    def test_mute_followup_notifications(self):
        # Bob's receive a notification and clicka on the mute link to
        # avoid additional comment messages on the same article.
        self.get_mute_followup_url(self.bobs_mutekey)
        # Alice sends 3rd comment to the article with follow-up
        data = {"name": "Alice", "email": "alice@example.com",
                "followup": True, "reply_to": 2, "level": 1, "order": 1,
                "comment": "And look at this and that..."}
        data.update(self.form.initial)
        self.client.post(reverse("comments-post-comment"), data=data)
        # Alice confirms her comment...
        self.assert_(self.mock_mailer.call_count == 4)
        alicekey = str(re.search(r'http://.+/confirm/(?P<key>[\S]+)',
                                 self.mock_mailer.call_args[0][1]).group("key"))
        self.get_confirm_comment_url(alicekey)  # confirm Alice's comment
        # Alice confirmed her comment, but this time Bob won't receive any
        # notification, neither do Alice being the sender
        self.assert_(self.mock_mailer.call_count == 4)


class HTMLDisabledMailTestCase(TestCase):
    def setUp(self):
        # Create an article and send a comment. Test method will chech headers
        # to see wheter messages has multiparts or not.
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="September", slug="september", body="John's September")
        self.form = django_comments.get_form()(self.article)

        # Bob sends 1st comment to the article with follow-up
        self.data = {"name": "Bob", "email": "bob@example.com",
                     "followup": True, "reply_to": 0, "level": 1, "order": 1,
                     "comment": "Nice September you had..."}
        self.data.update(self.form.initial)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_SEND_HTML_EMAIL=False)
    def test_mail_does_not_contain_html_part(self):
        with patch.multiple('django_comments_xtd.conf.settings',
                            COMMENTS_XTD_SEND_HTML_EMAIL=False):
            self.client.post(reverse("comments-post-comment"), data=self.data)
            self.assert_(self.mock_mailer.call_count == 1)
            self.assert_(self.mock_mailer.call_args[1]['html'] is None)

    def test_mail_does_contain_html_part(self):
        self.client.post(reverse("comments-post-comment"), data=self.data)
        self.assert_(self.mock_mailer.call_count == 1)
        self.assert_(self.mock_mailer.call_args[1]['html'] is not None)
