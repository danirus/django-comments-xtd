from django.utils.module_loading import import_string

import django_comments
from django_comments.feeds import LatestCommentFeed
from django_comments.signals import comment_was_posted, comment_will_be_posted


default_app_config = 'django_comments_xtd.apps.CommentsXtdConfig'


def get_model():
    from django_comments_xtd.conf import settings
    return import_string(settings.COMMENTS_XTD_MODEL)


def get_form():
    from django_comments_xtd.conf import settings
    return import_string(settings.COMMENTS_XTD_FORM_CLASS)


VERSION = (2, 8, 2, 'f', 0)  # following PEP 440


def get_version():
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version
