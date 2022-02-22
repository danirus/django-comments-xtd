"""
Django settings for project_stories project.

Generated by 'django-admin startproject' using Django 3.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path


PRODUCTION = bool(os.getenv("PRODUCTION", False))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bqac+=!uj4i@-1q-u#w=gy*q6b(y_5*nv84s4vbg#@5s+cq7nc'

SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if PRODUCTION else True

if PRODUCTION:
    ALLOWED_HOSTS = ['localhost',]
else:
    ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1']

ADMINS = (
    ('Alice Bloggs', 'admin@example.com'),
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'avatar',
    'rest_framework',
    'django_comments_xtd',
    'django_comments',
    'rosetta',

    'project_stories',  # To include the template tag.
    'users',
    'stories'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_stories.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project_stories.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'project_stories.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dcx-demo-qp',
            'USER': 'dcx-demo',
            'PASSWORD': 'dcx-demo',
            'HOST': 'dcx-postgres',
            'PORT': '5432'
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('nl', 'Dutch'),
    ('en', 'English'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('it', 'Italian'),
    ('no', 'Norwegian'),
    ('ru', 'Russian'),
    ('es', 'Spanish'),
    ('zh-hans', 'Simplified Chinese'),
)

LANGUAGE_COOKIE_NAME = "language"

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

if PRODUCTION:
    STATIC_URL = "http://localhost:8049/"
else:
    STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR.parent / "static"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / "media"

# Define the user model. The difference between 'users.User' and 'auth.User'
# is that the former doesn't include an 'username' attribute, and rather uses
# the email address.
AUTH_USER_MODEL = 'users.User'

SIGNUP_URL          = "/user/signup/"
LOGIN_URL           = "/user/login/"
LOGOUT_URL          = "/user/logout/"
LOGIN_REDIRECT_URL  = "/"
LOGOUT_REDIRECT_URL = "/"

COMMENTS_APP = "django_comments_xtd"

COMMENTS_HIDE_REMOVED = False

COMMENTS_XTD_SALT = b"w28dnq7czc1m+=l)=yiydar-r$$pnz#a5#22pjz_&5n%sq^kkr"
COMMENTS_XTD_CONFIRM_EMAIL = True   # Set to False to disable confirmation
COMMENTS_XTD_FROM_EMAIL = 'staff@example.com'
COMMENTS_XTD_CONTACT_EMAIL = 'staff@example.com'
COMMENTS_XTD_THREADED_EMAILS = False # default to True, use False to allow
                                     # other backend (say Celery based) send
                                     # your emails.

COMMENTS_XTD_API_USER_REPR = lambda user: user.name

COMMENTS_XTD_SEND_HTML_EMAIL = True

# This setting is to apply a maximum thread level of 1 to all apps by default.
COMMENTS_XTD_MAX_THREAD_LEVEL = 3

# This setting applies a maximum thread level of 1 only to the 'quotes.quote'
# app model. Useful in case you want to allow different levels of comment
# nesting to different app models.
# COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {
#     'quotes.quote': 3  # Meaning 4 levels: from 0 to 3.
# }

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'who_can_post': 'all',  # Valid values: "users", "all".
        'comment_flagging_enabled': True,
        'comment_reactions_enabled': True,
        'object_reactions_enabled': True,
    },
    'stories.story': {
        'check_input_allowed': 'stories.models.check_comments_input_allowed'
    }
}

# All HTML elements rendered by django-comments-xtd use the 'dcx' CSS selector,
# defined in 'django_comments_xtd/static/django_comments_xtd/css/comments.css'.
# You can alter the CSS rules applied to your comments adding your own custom
# selector to the following setting.
COMMENTS_XTD_CSS_CUSTOM_SELECTOR = "dcx dcx-custom"

# The theme dir, corresponds with any of the directories listed
# with the template directory: comments/themes/<theme_dir>.
COMMENTS_XTD_THEME_DIR = "avatar_in_thread"

COMMENTS_XTD_REACTIONS_ENUM = "project_stories.enums.ReactionEnum"

# Display up to the given number of comments in the last page to avoid
# creating another page containing only these amount of comments.
COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS = 4

# Number of comments per page. When <=0 pagination is disabled.
COMMENTS_XTD_ITEMS_PER_PAGE = 10

# This settings define the correction made to the popover JavaScript element
# and the tooltip element displayed in the Reactions area of each comment.
# The panel with the reaction choices is a popover, while the overlay with
# the name of the people who clicked on a specific reaction is a tooltip.
COMMENTS_XTD_REACTIONS_JS_OVERLAYS = {
    'default': {
        'popover': {
            'pos_bottom': 30,
            'pos_left': -6
        },
        'tooltip': {
            'pos_bottom': 30,
            'pos_left': 63
        }
    },
    # Given than stories.story display an avatar along with the comment,
    # the pos_left for both, the popover and tooltip, has to be adapted.
    'stories.story': {
        'popover': {
            'pos_bottom': 30,
            'pos_left': 10
        },
        'tooltip': {
            'pos_bottom': 30,
            'pos_left': 76
        }
    },
}

AVATAR_PROVIDERS = [
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.GravatarAvatarProvider',
]

AVATAR_GRAVATAR_DEFAULT = "identicon"

# Depending on the action the users.edit_avatar view redirects to
# 'avatar.views.add', 'avatar.views.change', or 'avatar.views.delete'.
AVATAR_ADD_TEMPLATE = "avatar/change.html"
AVATAR_DELETE_TEMPLATE = "avatar/change.html"


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
