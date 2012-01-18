from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase

from django_comments_xtd.models import XtdComment


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""
    
    def published(self):
        return self.get_query_set().filter(publish__lte=datetime.now())


class Article(models.Model):
    """Article, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        db_table = 'demo_articles'
        ordering = ('-publish',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('articles-article-detail', None, 
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})


class XtdCommentManagerTestCase(TestCase):

    def setUp(self):
        self.article_1 = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.article_2 = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        
    def test_for_app_models(self):
        # there is no comment yet posted to article_1 nor article_2
        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 0)

        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site = Site.objects.get(pk=1)

        # post one comment to article_1
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = self.article_1.id,
                                  content_object = self.article_1,
                                  site=site, comment="just a testing comment")

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 1)

        # post one comment to article_2
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = self.article_2.id,
                                  content_object = self.article_2,
                                  site=site, comment="yet another comment")

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 2)

        # post a second comment to article_2
        XtdComment.objects.create(content_type   = article_ct, 
                                  object_pk      = self.article_2.id,
                                  content_object = self.article_2,
                                  site=site, comment="and another one")

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 3)
