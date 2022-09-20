from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template import Context
from django.template import Template
from django.test import TestCase

from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article


class CommentTemplateTest(TestCase):
    def setUp(self) -> None:
        self.article_ct = ContentType.objects.get(
            app_label="tests",
            model="article"
        )
        self.site = Site.objects.get(pk=1)
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October...")

    def test_comment_template_with_comment(self):
        comment = XtdComment.objects.create(
            content_object=self.article,
            site=self.site,
            comment="comment 1 to article",
            is_removed=False,
            is_public=True,
        )
        template = '{% include "django_comments_xtd/comment.html" %}'
        rendered_html = Template(template).render(Context({'comment': comment}))
        self.assertTrue('comment 1 to article' in rendered_html)
        self.assertTrue(self.article.get_absolute_url() in rendered_html)

    def test_comment_template_with_removed_comment(self):
        comment = XtdComment.objects.create(
            content_object=self.article,
            site=self.site,
            comment="comment 1 to article",
            is_removed=True,
            is_public=True,
        )
        template = '{% include "django_comments_xtd/comment.html" %}'
        rendered_html = Template(template).render(Context({'comment': comment}))
        self.assertTrue('This comment has been removed.' in rendered_html)
        self.assertFalse('comment 1 to article' in rendered_html)
