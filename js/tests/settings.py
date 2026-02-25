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
    "django_comments_xtd",
    "django_comments",
    "shared.users",
    "tests.specs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.urls"

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": PROJECT_DIR / "db.sqlite3",
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

TIME_ZONE = "Europe/Berlin"

STATIC_URL = "/static/"

STATIC_ROOT = PROJECT_DIR / "static"

# Additional locations of static files
STATICFILES_DIRS = [
    PROJECT_DIR.parents[1] / "example" / "shared" / "frontend",
    PROJECT_DIR.parents[1] / "js" / "src",  # To load apps index.js.
    PROJECT_DIR.parents[1],  # To load node_modules.
]


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

AUTH_USER_MODEL = "users.User"

SIGNUP_URL = "/user/signup/"
LOGIN_URL = "/user/login/"
LOGOUT_URL = "/user/logout/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Fill in actual EMAIL settings above, and comment out the
# following line to let this django demo sending emails
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ------------------------------------------------------------
# Comments related settings.

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

# By default ContentType.objects.get_for_model pass True in the
# keyword argument `for_concrete_model`. If you use Proxy models
# you might want to make django-comments-xtd use the proxy models
# instead. In such a case switch this setting to False.
COMMENTS_XTD_FOR_CONCRETE_MODEL = False

# Define what commenting features a pair app_label.model can have.
COMMENTS_XTD_APP_MODEL_CONFIG = {
    "default": {
        "who_can_post": "all",
        "max_thread_level": 0,
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": True,
        "comments_voting_enabled": True,
        "list_order": ("-thread__score", "thread__id", "order"),
    },
}

# How many users are listed when hovering a reaction.
COMMENTS_XTD_MAX_USERS_IN_TOOLTIP = 10
