from datetime import datetime

from django.db import models
from django.urls import reverse

from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment
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

    def get_absolute_url(self):
        return reverse(
            'article-detail',
            kwargs={'year': self.publish.year,
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


def authorize_api_post_comment(sender, comment, request, **kwargs):
    if (
        (request.user and request.user.is_authenticated) or
        (request.auth and request.auth == settings.MY_DRF_AUTH_TOKEN)
    ):
        return True
    else:
        return False


class MyComment(XtdComment):
    title = models.CharField(max_length=256)
