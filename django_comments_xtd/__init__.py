import django
from django_comments_xtd.conf import settings

if django.VERSION[:2] <= (1, 5): # Django <= 1.5
    from django_comments_xtd.compat import import_by_path as import_string
elif (1, 6) <= django.VERSION[:2] < (1, 8): # Django v1.6.x and 1.7.x
    from django.utils.module_loading import import_by_path as import_string
else: # Django >= 1.8
    from django.utils.module_loading import import_string
    

# While there's official support for Django version prior to 1.8
try:
    import django_comments
    from django_comments.feeds import LatestCommentFeed
    from django_comments.signals import comment_was_posted
except ImportError:
    import django.contrib.comments as django_comments
    from django.contrib.comments.feeds import LatestCommentFeed
    from django.contrib.comments.signals import comment_was_posted


default_app_config = 'django_comments_xtd.apps.CommentsXtdConfig'
    
def get_model():
    return import_string(settings.COMMENTS_XTD_MODEL)

def get_form():
    return import_string(settings.COMMENTS_XTD_FORM_CLASS)

VERSION = (1, 6, 2, 'f', 0) # following PEP 440

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version
