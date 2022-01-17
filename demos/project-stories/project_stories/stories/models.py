from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone


class PublicManager(models.Manager):
    """Returns published stories that are not yet in the future."""

    def published(self):
        return self.get_queryset().filter(published_time__lte=timezone.now())


class Story(models.Model):
    """Stories that may accept comments."""

    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique_for_date='published_time')
    body = models.TextField('body')
    allow_comments = models.BooleanField(default=True)
    published_time = models.DateTimeField(default=timezone.now)

    objects = PublicManager()

    class Meta:
        verbose_name_plural = "stories"
        ordering = ('published_time',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'story-detail',
            kwargs={'year': self.published_time.year,
                    'month': int(self.published_time.strftime('%m').lower()),
                    'day': self.published_time.day,
                    'slug': self.slug})


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