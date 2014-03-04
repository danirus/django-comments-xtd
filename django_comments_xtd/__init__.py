from django_comments_xtd.conf import settings
try:
    from django.utils.module_loading import import_by_path # Django >= 1.6
except ImportError:
    from django_comments_xtd.compat import import_by_path # Django <= 1.5


def get_model():
    return import_by_path(settings.COMMENTS_XTD_MODEL)

def get_form():
    return import_by_path(settings.COMMENTS_XTD_FORM_CLASS)

VERSION = (1, 3, 0, 'a', 1) # following PEP 440

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version
