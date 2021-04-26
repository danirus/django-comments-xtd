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
