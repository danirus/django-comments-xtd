from __future__ import unicode_literals

import os
import imp


PRJ_PATH = os.path.abspath(os.path.curdir)

DEBUG = True

ADMINS = (
    ('Joe, the Administrator', 'joe.bloggs@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     'django_comments_xtd',
        'USER':     '',
        'PASSWORD': '',
        'HOST':     '',
        'PORT':     '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'
USE_TZ = False
USE_L10N = False

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = 'v2824l&2-n+4zznbsk9c-ap5i)b3e8b+%*a=dxqlahm^%)68jn'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'django_comments_xtd.tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), "templates"),
            os.path.join(os.path.dirname(__file__), "..", "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ]
        }
    }
]

try:
    imp.find_module('django_comments')
    django_comments = 'django_comments'
except ImportError:
    django_comments = 'django.contrib.comments'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'rest_framework',

    'django_comments_xtd',
    'django_comments_xtd.tests',
    django_comments,
]
COMMENTS_APP = "django_comments_xtd"

DEFAULT_FROM_EMAIL = "Alice Bloggs <alice@example.com>"

COMMENTS_XTD_CONFIRM_EMAIL = True
COMMENTS_XTD_SALT = b"es-war-einmal-una-bella-princesa-in-a-beautiful-castle"
COMMENTS_XTD_MAX_THREAD_LEVEL = 2
COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {'tests.diary': 0}

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'tests.diary': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    }
}

MY_DRF_AUTH_TOKEN = "08d9fd42468aebbb8087b604b526ff0821ce4525"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'django_comments_xtd.tests.apiauth.APIRequestAuthentication'
   ]
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
