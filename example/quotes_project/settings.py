import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()

DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

ADMINS = (("Alice Bloggs", "alice@example.com"),)
MANAGERS = ADMINS

ALLOWED_HOSTS = ["localhost"]

INTERNAL_IPS = ["127.0.0.1"]

SITE_ID = 1

SECRET_KEY = "v2824l&2-n+4zznbsk9c-ap5i)b3e8b+%*a=dxqlahm^%)68jn"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "django_comments_xtd",
    "django_comments",
    "shared.users",
    "quotes",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "quotes_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "quotes_project.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": PROJECT_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PWD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en"

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = "UTC"

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

STATIC_URL = "/static/"

STATIC_ROOT = PROJECT_DIR / "static"

# Additional locations of static files
STATICFILES_DIRS = [
    PROJECT_DIR.parent / "shared" / "frontend"
]


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Define the user model. The difference between 'users.User' and 'auth.User'
# is that the former doesn't include an 'username' attribute, and rather uses
# the email address.
AUTH_USER_MODEL = "users.User"

SIGNUP_URL = "/user/signup/"
LOGIN_URL = "/user/login/"
LOGOUT_URL = "/user/logout/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# EMAIL_HOST          = "smtp.gmail.com"
# EMAIL_PORT          = "587"
# EMAIL_HOST_USER     = "username@gmail.com"
# EMAIL_HOST_PASSWORD = ""
# EMAIL_USE_TLS       = True # Yes for Gmail
# DEFAULT_FROM_EMAIL  = "Alice Bloggs <alice@example.com>"
# SERVER_EMAIL        = DEFAULT_FROM_EMAIL

# Fill in actual EMAIL settings above, and comment out the
# following line to let this django demo sending emails
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

COMMENTS_APP = "django_comments_xtd"

COMMENTS_HIDE_REMOVED = False

COMMENTS_XTD_CONFIRM_EMAIL = True  # Set to False to disable confirmation
COMMENTS_XTD_SALT = b"es-war-einmal-una-bella-princesa-in-a-beautiful-castle"
COMMENTS_XTD_FROM_EMAIL = "noreply@example.com"
COMMENTS_XTD_CONTACT_EMAIL = "helpdesk@example.com"

# COMMENTS_XTD_THREADED_EMAILS defaults to True, use False to allow
# other backend (say Celery based) send your emails.
COMMENTS_XTD_THREADED_EMAILS = False

# Define a function to return the user representation. Used by
# the web API to represent user strings in HTTP responses.
def _comments_xtd_fn_user_repr(user):
    return user.name
COMMENTS_XTD_FN_USER_REPR = _comments_xtd_fn_user_repr

# Make django-comments-xtd send emails in HTML format too.
COMMENTS_XTD_SEND_HTML_EMAIL = True

# Maximum Thread Level.
COMMENTS_XTD_MAX_THREAD_LEVEL = 1

# Maximum Thread Level per app.model basis.
# In this example project it makes no sense, as the previous setting
# already establishes the maximum thread level to 1 for the only model
# that can receive comments: the `quotes.quote` model.
COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {
    "quotes.quote": 1,
}

# Define what commenting features a pair app_label.model can have.
COMMENTS_XTD_APP_MODEL_OPTIONS = {
    "quotes.quote": {
        "who_can_post": "all",
        "allow_flagging": True,
        "allow_feedback": True,
        "show_feedback": True,
    },
}

# How many users are listed when hovering a reaction.
COMMENTS_XTD_MAX_USERS_IN_TOOLTIP = 10

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.sql.SQLPanel",
]
