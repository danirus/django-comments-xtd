from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone


from django_comments_xtd.moderation import moderator, SpamModerator


class PublicManager(models.Manager):
    """Returns published quotes that are not in the future."""

    def published(self):
        return self.get_queryset().filter(published_time__lte=timezone.now())


class Quote(models.Model):
    """Quote, that accepts comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='published_time')
    quote = models.TextField('quote')
    author = models.CharField('author', max_length=255)
    url_source = models.URLField('url source', blank=True, null=True)
    allow_comments = models.BooleanField('allow comments', default=True)
    published_time = models.DateTimeField('published time',
                                          default=timezone.now)

    objects = PublicManager()

    class Meta:
        db_table = 'comp_quotes'
        ordering = ('-published_time',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('quote-detail', kwargs={'slug': self.slug})


class QuoteCommentModerator(SpamModerator):
    email_notification = True
    auto_moderate_field = 'published_time'
    moderate_after = 365


moderator.register(Quote, QuoteCommentModerator)


def check_comments_input_allowed(obj):
    """
    Return False if obj's published_time is older than 2 years.
    """
    obj_date = obj.published_time.date()
    obj_time = obj.published_time.time()
    in2years_date = date(obj_date.year + 2, obj_date.month, obj_date.day)
    in2years = timezone.make_aware(datetime.combine(in2years_date, obj_time))
    if timezone.now() > in2years:
        return False
    else:
        return True