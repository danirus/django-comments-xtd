from django.db import models
from django.urls import reverse
from django.utils import timezone


class PublicManager(models.Manager):
    """Returns published diary entries that are not in the future."""

    def published(self, reverse=False):
        return self.get_queryset().filter(publish__lte=timezone.now())


class Diary(models.Model):
    """Short diary entries."""

    body = models.TextField("body")
    allow_comments = models.BooleanField('allow comments', default=True)
    publish = models.DateTimeField('publish', default=timezone.now)

    objects = PublicManager()

    class Meta:
        db_table = 'comp_diary'
        ordering = ('-publish',)

    def __str__(self):
        if len(self.body) > 20:
            return self.body[0:20] + "..."
        else:
            return self.body

    def get_absolute_url(self):
        return reverse(
            'diary-day',
            kwargs={'year': self.publish.year,
                    'month': self.publish.strftime('%b').lower(),
                    'day': self.publish.day}
        ) + "#entry-%d" % self.id