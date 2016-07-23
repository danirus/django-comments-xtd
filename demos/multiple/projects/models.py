#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class ProjectManager(models.Manager):
    """Returns active projects."""
    
    def active(self):
        return self.get_query_set().filter(is_active=True)


@python_2_unicode_compatible
class Project(models.Model):
    """Project that accepts comments."""

    class Meta:
        db_table = 'projects'
        ordering = ('project_name',)

    project_name = models.CharField(blank=False, max_length=18)
    slug = models.SlugField(primary_key=True)
    short_description = models.CharField(blank=False, max_length=110)
    is_active = models.BooleanField()

    objects = ProjectManager()

    def __str__(self):
        return "%s" % (self.project_name)

    @models.permalink
    def get_absolute_url(self):
        return ('projects-project-detail', [self.slug])


class ReleaseManager(models.Manager):
    """Returns active published releases that are not in the future."""
    
    def published(self):
        return self.get_query_set().filter(publish__lte=datetime.now(), 
                                           is_active=True)


@python_2_unicode_compatible
class Release(models.Model):
    """Project evolution is divided in releases."""

    class Meta:
        db_table = 'releases'
        unique_together = ('project', 'slug',)
        ordering = ('project', 'release_name',)

    project = models.ForeignKey(Project)
    release_name = models.CharField(blank=False, max_length=18)
    slug = models.SlugField(max_length=255)
    release_date = models.DateTimeField(default=datetime.today)
    body = models.TextField(max_length=2048, help_text=_("Release description"))
    is_active = models.BooleanField()
    allow_comments = models.BooleanField(default=True)
    
    def __str__(self):
        return "%s/%s" % (self.project.project_name, self.release_name)

    @models.permalink
    def get_absolute_url(self):
        return ('projects-release-detail', [self.project.slug, self.slug])
