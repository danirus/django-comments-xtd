#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.abspath(os.path.curdir)

DEBUG = True

INTERNAL_IPS = [
    '127.0.0.1'
]

ADMINS = (
    ('Alice Bloggs', 'alice@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/'
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'v2824l&2-n+4zznbsk9c-ap5i)b3e8b+%*a=dxqlahm^%)68jn'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
	    'DIRS': [
	        os.path.join(os.path.dirname(__file__), "templates"),
	    ],
        'APP_DIRS': True,
	    'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'django_markdown2',
    'articles',
    'mycomments',
    'django_comments_xtd',
    'django_comments',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# EMAIL_HOST          = "smtp.gmail.com"
# EMAIL_PORT          = "587"
# EMAIL_HOST_USER     = "username@gmail.com"
# EMAIL_HOST_PASSWORD = ""
# EMAIL_USE_TLS       = True # Yes for Gmail
# DEFAULT_FROM_EMAIL  = "Alice Bloggs <alice@example.com>"
# SERVER_EMAIL        = DEFAULT_FROM_EMAIL

# Fill in actual EMAIL settings above, and comment out the
# following line to let this django demo sending emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMMENTS_APP = "django_comments_xtd"
COMMENTS_XTD_CONFIRM_EMAIL = True # Set to True to request confirmations
COMMENTS_XTD_SALT = b"es-war-einmal-una-bella-princesa-in-a-beautiful-castle"
COMMENTS_XTD_FROM_EMAIL = 'noreply@example.com'
COMMENTS_XTD_CONTACT_EMAIL = 'helpdesk@example.com'
COMMENTS_XTD_MAX_THREAD_LEVEL = 2
COMMENTS_XTD_THREADED_EMAILS = False # default to True, use False to allow
                                     # other backend (say Celery based) send
                                     # your emails.

COMMENTS_XTD_MODEL = 'mycomments.models.MyComment'
COMMENTS_XTD_FORM_CLASS = 'mycomments.forms.MyCommentForm'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.sql.SQLPanel',
]
