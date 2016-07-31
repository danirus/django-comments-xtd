from datetime import datetime

from django.db import models
from django.db.models import permalink

from django_comments_xtd.moderation import moderator, XtdCommentModerator


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

    @permalink
    def get_absolute_url(self):
        return ('articles-article-detail', None,
                {'year': self.publish.year,
                 'month': int(self.publish.strftime('%m').lower()),
                 'day': self.publish.day,
                 'slug': self.slug})


class Diary(models.Model):
    """Diary, that accepts comments."""
    body = models.TextField('body')
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=datetime.now)

    objects = PublicManager()

    class Meta:
        db_table = 'demo_diary'
        ordering = ('-publish',)


class DiaryCommentModerator(XtdCommentModerator):
    email_notification = True
    enable_field = 'allow_comments'
    auto_moderate_field = 'publish'
    moderate_after = 2
    removal_suggestion_notification = True

moderator.register(Diary, DiaryCommentModerator)
