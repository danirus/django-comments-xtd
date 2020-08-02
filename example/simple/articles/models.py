#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from django_comments_xtd.conf import settings
from django_comments_xtd.signals import should_request_be_authorized


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""

    if django.VERSION < (1, 6):
        get_queryset = models.Manager.get_query_set
    
    def published(self):
        return self.get_queryset().filter(publish__lte=timezone.now())


class Article(models.Model):
    """Article, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=timezone.now)

    objects = PublicManager()

    class Meta:
        db_table = 'simple_articles'
        ordering = ('-publish',)

    def __str__(self):
        return '%s' % self.title

    def get_absolute_url(self):
        return reverse(
            'articles-article-detail',
            kwargs={'year': self.publish.year,
                    'month': int(self.publish.strftime('%m').lower()),
                    'day': self.publish.day,
                    'slug': self.slug})
