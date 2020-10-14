from __future__ import unicode_literals

import json
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse
from django.test import TestCase as DjangoTestCase

from rest_framework.test import APIRequestFactory, APITestCase

from django_comments_xtd import django_comments, get_model
from django_comments_xtd.api.views import (
    CommentCount, CommentCreate, CommentList)
from django_comments_xtd.models import (
    XtdComment, publish_or_withhold_on_pre_save)
from django_comments_xtd.tests.models import Article, Diary, MyComment
from django_comments_xtd.tests.utils import post_comment
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3)


app_model_options_mock = {
    'tests.article': {
        'who_can_post': 'users'
    }
}


factory = APIRequestFactory()


class CommentCreateTestCase(DjangoTestCase):
    def setUp(self):
        patcher = patch('django_comments_xtd.views.send_mail')
        self.mock_mailer = patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.form = django_comments.get_form()(self.article)

    def test_post_returns_2xx_response(self):
        data = {"name": "Bob", "email": "fulanito@detal.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.mock_mailer.call_count, 1)

    def test_post_returns_4xx_response(self):
        # It uses an authenticated user, but the user has no mail address.
        self.user = User.objects.create_user("bob", "", "pwd")
        data = {"name": "", "email": "",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data, auth_user=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('name' in response.data)
        self.assertTrue('email' in response.data)
        self.assertEqual(self.mock_mailer.call_count, 0)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_APP_MODEL_OPTIONS=app_model_options_mock)
    def test_post_returns_unauthorize_response(self):
        data = {"name": "Bob", "email": "fulanito@detal.com",
                "followup": True, "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal eine kleine...",
                "honeypot": ""}
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.rendered_content, b'"User not authenticated"')
        self.assertEqual(self.mock_mailer.call_count, 0)


_xtd_model = "django_comments_xtd.tests.models.MyComment"


class CommentCountTestCase(APITestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")

    def _send_request(self):
        kwargs = {"content_type": "tests-article", "object_pk": "1"}
        req = factory.get(reverse('comments-xtd-api-count', kwargs=kwargs))
        view = CommentCount.as_view()
        return view(req, **kwargs)

    def test_get_count_shall_be_0(self):
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":0}')

    def test_get_count_shall_be_2(self):
        thread_test_step_1(self.article)
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MODEL=_xtd_model)
    def test_get_count_for_custom_comment_model_shall_be_2(self):
        thread_test_step_1(self.article, model=MyComment,
                           title="Can't be empty 1")
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_get_count_for_comments_sent_to_different_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')
        thread_test_step_1(self.article)
        thread_test_step_1(self.article, site=site2)
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_count_for_HIDE_REMOVED_case_1(self):
        # To find out what are the cases 1, 2 and 3, read the docs settings
        # page, section COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED.
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False.
        # Therefore the count should return 1 -> cm2. cm1 is hidden.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":1}')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_count_for_HIDE_REMOVED_case_2(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        #
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_get_count_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        #
        # These two lines create the following comments:
        #
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()

        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 must remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":4}')

        # Re-connect the function for the following tests.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)


class CommentListTestCase(APITestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")

    def _send_request(self):
        kwargs = {"content_type": "tests-article", "object_pk": "1"}
        req = factory.get(reverse('comments-xtd-api-list', kwargs=kwargs))
        view = CommentList.as_view()
        return view(req, **kwargs)

    def test_get_list(self):
        thread_test_step_1(self.article)  # Sends 2 comments.
        thread_test_step_2(self.article)  # Sends 2 comments.
        thread_test_step_3(self.article)  # Sends 1 comment.
        # -> content:   cmt.id  thread_id  parent_id  level  order
        # cm1,   # ->      1         1          1        0      1
        # cm3,   # ->      3         1          1        1      2
        # cm4,   # ->      4         1          1        1      3
        # cm2,   # ->      2         2          2        0      1
        # cm5    # ->      5         2          2        1      2
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 5)
        for cm, cm_id in zip(data, [1, 3, 4, 2, 5]):
            self.assertEqual(cm['id'], cm_id)

    # Missing enhancement: extend the capacity to customize the comment model
    # to the API, so that a comment model can be used in combination with its
    # own serializer, and test it here.

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_get_list_for_a_second_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')

        # Send nested comments to the article in the site1.
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)

        # Send some nested comments to the article in the site2.
        thread_test_step_1(self.article, site=site2)

        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 2)
        for cm, cm_id in zip(data, [6, 7]):
            self.assertEqual(cm['id'], cm_id)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_list_for_HIDE_REMOVED_case_1(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing cm1, both cm3 and cm4 have is_public=False.
        # Therefore the list of comments should contain only cm2.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 2)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_list_for_HIDE_REMOVED_case_2(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        #
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 2)
        for cm, cm_id in zip(data, [1, 2]):
            self.assertEqual(cm['id'], cm_id)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_get_list_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 4)
        for cm, cm_id in zip(data, [1, 3, 4, 2]):
            self.assertEqual(cm['id'], cm_id)
        # Re-connect the function for the following tests.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)
