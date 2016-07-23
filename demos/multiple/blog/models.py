#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

import django
from django.db import models
from django.db.models import permalink
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""
    
    if django.VERSION < (1, 6):
        get_queryset = models.Manager.get_query_set

    def published(self):
        return self.get_queryset().filter(publish__lte=datetime.now())


@python_2_unicode_compatible
class Story(models.Model):
    """Story that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        db_table = 'stories'
        ordering = ('-publish',)
        verbose_name = _('story')
        verbose_name_plural = _('stories')

    def __str__(self):
        return '%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog-story-detail', None, 
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})


@python_2_unicode_compatible
class Quote(models.Model):
    """Quote that accepts comments."""

    title = models.CharField('title', max_length=100)
    slug = models.SlugField('slug', max_length=255, unique=True)
    quote = models.TextField('quote')
    author = models.CharField('author', max_length=255)
    url_source = models.URLField('url source', blank=True, null=True)
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        db_table = 'quotes'
        ordering = ('-publish',)
        verbose_name = _('quote')
        verbose_name_plural = _('quotes')

    def __str__(self):
        return '%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog-quote-detail', (), {'slug': self.slug})
