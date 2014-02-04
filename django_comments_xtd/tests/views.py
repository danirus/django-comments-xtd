from __future__ import unicode_literals

import re
from mock import patch
from datetime import datetime

# from django.conf import settings
from django.contrib import comments
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core import mail
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponse
from django.test import TestCase
# from django.test.utils import override_settings

from django_comments_xtd import signals, signed
from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment, TmpXtdComment
from django_comments_xtd.tests.models import Article, Diary
from django_comments_xtd.views import on_comment_was_posted
from django_comments_xtd.utils import mail_sent_queue


def dummy_view(request, *args, **kwargs):
    return HttpResponse("Got it")


class OnCommentWasPostedTestCase(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="September", 
                                              slug="september",
                                              body="What I did on September...")
        self.form = comments.get_form()(self.article)
        
    def post_valid_data(self, wait_mail=True):
        data = {"name":"Bob", "email":"bob@example.com", "followup": True, 
                "reply_to": 0, "level": 1, "order": 1,
                "comment":"Es war einmal iene kleine..."}
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"), 
                                        data=data, follow=True)
        if wait_mail and mail_sent_queue.get(block=True):
            pass

    def test_post_as_authenticated_user(self):
        auth_user = User.objects.create_user("bob", "bob@example.com", "pwd")
        self.client.login(username="bob", password="pwd")
        self.assertEqual(len(mail.outbox), 0)
        self.post_valid_data(wait_mail=False)
        # no confirmation email sent as user is authenticated
        self.assertEqual(len(mail.outbox), 0) 

    def test_confirmation_email_is_sent(self):
        self.assertEqual(len(mail.outbox), 0)
        self.post_valid_data()
        self.assertEqual(len(mail.outbox), 1)
        self.assertTemplateUsed(self.response, "comments/posted.html")


class ConfirmCommentTestCase(TestCase):
    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(title="September", 
                                              slug="september",
                                              body="What I did on September...")
        self.form = comments.get_form()(self.article)
        data = {"name": "Bob", "email": "bob@example.com", "followup": True, 
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal iene kleine..." }
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

        self.assertEqual(self.mock_mailer.call_count, 1) # sent during setUp
        signals.confirmation_received.connect(on_signal)
        self.get_confirm_comment_url(self.key)
        # mailing avoided by on_signal:
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.assertTemplateUsed(self.response, 
                                "django_comments_xtd/discarded.html")

    def test_comment_is_created_and_view_redirect(self):
        # testing that visiting a correct confirmation URL creates a XtdComment
        # and redirects to the article detail page
        Site.objects.get_current().domain = "testserver" # django bug #7743
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
        self.assert_(comment != None)
        self.assertRedirects(self.response, self.article.get_absolute_url())

    def test_notify_comment_followers(self):
        # send a couple of comments to the article with followup=True and check
        # that when the second comment is confirmed a followup notification 
        # email is sent to the user who sent the first comment
        self.assertEqual(self.mock_mailer.call_count, 1)
        self.get_confirm_comment_url(self.key)
        # no comment followers yet:
        self.assertEqual(self.mock_mailer.call_count, 1)
        # send 2nd comment
        self.form = comments.get_form()(self.article)
        data = {"name":"Alice", "email":"alice@example.com", "followup": True, 
                "reply_to": 0, "level": 1, "order": 1,
                "comment":"Es war einmal eine kleine..." }
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"), 
                                        data=data)
        self.assertEqual(self.mock_mailer.call_count, 2)
        self.key = re.search(r'http://.+/confirm/(?P<key>[\S]+)', 
                             self.mock_mailer.call_args[0][1]).group("key")
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.assert_(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assert_(self.mock_mailer.call_args[0][1].find("There is a new comment following up yours.") > -1)

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

        self.form = comments.get_form()(diary)
        data = {"name": "Charlie", "email": "charlie@example.com", 
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine..." }
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

        self.form = comments.get_form()(self.article)
        data = {"name":"Alice", "email":"alice@example.com", "followup": True, 
                "reply_to": 0, "level": 1, "order": 1,
                "comment":"Es war einmal iene kleine..." }
        data.update(self.form.initial)
        self.response = self.client.post(reverse("comments-post-comment"), 
                                        data=data)
        self.assertEqual(self.mock_mailer.call_count, 3)
        self.key = re.search(r'http://.+/confirm/(?P<key>[\S]+)', 
                             self.mock_mailer.call_args[0][1]).group("key")
        self.get_confirm_comment_url(self.key)
        self.assertEqual(self.mock_mailer.call_count, 4)
        self.assert_(self.mock_mailer.call_args[0][3] == ["bob@example.com"])
        self.assert_(self.mock_mailer.call_args[0][1].find("There is a new comment following up yours.") > -1)

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
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = article.id,
                                  content_object = article,
                                  site           = site, 
                                  comment        ="comment 1 to article",
                                  submit_date    = datetime.now())

        # post Comment 2 to article, level 1
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = article.id,
                                  content_object = article,
                                  site           = site, 
                                  comment        ="comment 1 to comment 1",
                                  submit_date    = datetime.now(),
                                  parent_id      = 1)

        # post Comment 3 to article, level 2 (max according to test settings)
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = article.id,
                                  content_object = article,
                                  site           = site, 
                                  comment        ="comment 1 to comment 1",
                                  submit_date    = datetime.now(),
                                  parent_id      = 2)

    def test_reply_renders_max_thread_level_template(self):
        response = self.client.get(reverse("comments-xtd-reply", 
                                                kwargs={"cid": 3}))
        self.assertTemplateUsed(response, 
                                "django_comments_xtd/max_thread_level.html")
