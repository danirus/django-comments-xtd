from __future__ import unicode_literals

from datetime import datetime

import django
from django.db import models
from django.db.models import permalink
from django.utils.encoding import python_2_unicode_compatible

from django_comments_xtd.moderation import moderator, SpamModerator
from example.articles.badwords import badwords


class PublicManager(models.Manager):
    """Returns published articles that are not in the future."""
    
    if django.VERSION < (1, 6):
        get_queryset = models.Manager.get_query_set

    def published(self):
        return self.get_queryset().filter(publish__lte=datetime.now())


@python_2_unicode_compatible
class Article(models.Model):
    """Article, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='publish')
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('articles-article-detail', None, 
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})


class BadWordsModerator(SpamModerator):
    def moderate(self, comment, content_object, request):
        # Make a dictionary where the keys are the words of the message and
        # the values are their relative position in the message. 
        msg = dict([(w, i) for i, w in enumerate(comment.comment.split())])
        for badword in badwords:
            if isinstance(badword, str):
                if badword in msg:
                    return True
            else:
                lastindex = -1
                for subword in badword:
                    if subword in msg:
                        if lastindex > -1:
                            if msg[subword] == (lastindex + 1):
                                lastindex = msg[subword]
                        else:
                            lastindex = msg[subword]
                    else:
                        break
                if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                    print("Comment shouldn't be public")
                    return True

moderator.register(Article, BadWordsModerator)
