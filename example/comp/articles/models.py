from __future__ import unicode_literals

import django
from django.db import models
from django.db.models import permalink
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""
    
    def published(self):
        return self.get_queryset().filter(publish__lte=timezone.now())


@python_2_unicode_compatible
class Article(models.Model):
    """Article, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=timezone.now)

    objects = PublicManager()

    class Meta:
        db_table = 'comp_articles'
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('articles-article-detail', (),
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})
