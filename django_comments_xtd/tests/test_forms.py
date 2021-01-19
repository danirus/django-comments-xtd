from django.test import TestCase

from django_comments_xtd import django_comments
from django_comments_xtd.models import TmpXtdComment
from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.tests.models import Article

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class GetFormTestCase(TestCase):

    def test_get_form(self):
        # check function django_comments_xtd.get_form retrieves the due class
        self.assertTrue(django_comments.get_form() == XtdCommentForm)


class XtdCommentFormTestCase(TestCase):

    def setUp(self):
        self.article = Article.objects.create(title="September",
                                              slug="september",
                                              body="What I did on September...")
        self.form = django_comments.get_form()(self.article)

    def test_get_comment_model(self):
        # check get_comment_model retrieves the due model class
        self.assertTrue(self.form.get_comment_model() == TmpXtdComment)

    def test_get_comment_create_data(self):
        # as it's used in django_comments.views.comments
        data = {"name": "Daniel",
                "email": "danirus@eml.cc",
                "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal iene kleine..."}
        data.update(self.form.initial)
        form = django_comments.get_form()(self.article, data)
        self.assertTrue(self.form.security_errors() == {})
        self.assertTrue(self.form.errors == {})
        comment = form.get_comment_object()

        # it does have the new field 'followup'
        self.assertTrue("followup" in comment)

    @patch.multiple('django_comments_xtd.conf.settings',
                COMMENTS_XTD_DEFAULT_FOLLOW_UP=True)
    def test_setting_COMMENTS_XTD_DEFAULT_FOLLOW_UP_works(self):
                # as it's used in django_comments.views.comments
        data = {"name": "Daniel",
                "email": "danirus@eml.cc",
                "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmal iene kleine..."}
        data.update(self.form.initial)
        form = django_comments.get_form()(self.article, data)
        comment = form.get_comment_object()

        # it does have the new field 'followup'
        self.assertTrue("followup" in comment)
        # But we don't have it in form, it comes from the settings
        self.assertFalse('followup' in form)
