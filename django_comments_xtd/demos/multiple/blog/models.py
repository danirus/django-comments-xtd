from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""
    
    def published(self):
        return self.get_query_set().filter(publish__lte=datetime.now())


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

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog-story-detail', None, 
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})


class Quote(models.Model):
    """Quote that accepts comments."""

    title = models.CharField('title', max_length=100)
    slug = models.SlugField('slug', max_length=255, unique=True)
    quote = models.TextField('quote')
    author = models.CharField('author', max_length=255)
    url_source = models.URLField('url source', verify_exists=False,
                                 blank=True, null=True)
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        db_table = 'quotes'
        ordering = ('-publish',)
        verbose_name = _('quote')
        verbose_name_plural = _('quotes')

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog-quote-detail', (), {'slug': self.slug})
