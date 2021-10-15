from .settings import *
try:
    from .settings_local import *
except ImportError:
    pass


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'dcx3demo',
    #     'USER': 'dcx3demo',
    #     'PASSWORD': 'dcx3demo',
    #     'HOST': 'localhost',
    #     'PORT': '5432'
    # },
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'dcx3demo',
    #     'USER': 'dcx3demo',
    #     'PASSWORD': 'dcx3demo',
    #     'HOST': 'localhost',
    #     'PORT': '3306'
    # }
}

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
    'rosetta'
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.sql.SQLPanel',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

