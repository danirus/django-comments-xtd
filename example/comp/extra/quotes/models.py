from __future__ import unicode_literals

import django
from django.db import models
from django.urls import reverse
from django.utils import timezone


from django_comments_xtd.moderation import moderator, SpamModerator


class PublicManager(models.Manager):
    """Returns published quotes that are not in the future."""
    
    def published(self):
        return self.get_queryset().filter(publish__lte=timezone.now())


class Quote(models.Model):
    """Quote, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    quote = models.TextField('quote')
    author = models.CharField('author', max_length=255)
    url_source = models.URLField('url source', blank=True, null=True)    
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=timezone.now)

    objects = PublicManager()

    class Meta:
        db_table = 'comp_quotes'
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('quotes-quote-detail', kwargs={'slug': self.slug})


class QuoteCommentModerator(SpamModerator):
    email_notification = True
    auto_moderate_field = 'publish'
    moderate_after = 365


moderator.register(Quote, QuoteCommentModerator)
