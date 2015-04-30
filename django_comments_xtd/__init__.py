from django import VERSION as DJANGO_VERSION
from django_comments_xtd.conf import settings

if DJANGO_VERSION[1] <= 5: # Django <= 1.5
    from django_comments_xtd.compat import import_by_path as import_string
elif 6 <= DJANGO_VERSION[1] < 8: # Django v1.6.x and 1.7.x
    from django.utils.module_loading import import_by_path as import_string
else: # Django >= 1.8
    from django.utils.module_loading import import_string
    

# While there's official support for Django version prior to 1.8
try:
    import django_comments
    import django_comments.urls as django_comments_urls
    from django_comments.models import Comment
    from django_comments.feeds import LatestCommentFeed
    from django_comments.forms import CommentForm
    from django_comments.signals import comment_was_posted
except ImportError:
    import django.contrib.comments as django_comments
    import django.contrib.comments.urls as django_comments_urls
    from django.contrib.comments import get_form
    from django.contrib.comments.models import Comment
    from django.contrib.comments.feeds import LatestCommentFeed
    from django.contrib.comments.forms import CommentForm
    from django.contrib.comments.signals import comment_was_posted

    
def get_model():
    return import_string(settings.COMMENTS_XTD_MODEL)

def get_form():
    return import_string(settings.COMMENTS_XTD_FORM_CLASS)

VERSION = (1, 4, 0, 'b', 2) # following PEP 440

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version
