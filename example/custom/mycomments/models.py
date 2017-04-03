from django.db import models

from django_comments_xtd.models import XtdComment


class MyComment(XtdComment):
    title = models.CharField(max_length=256)
