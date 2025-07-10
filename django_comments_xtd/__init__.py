# ruff:noqa: I001

default_app_config = "django_comments_xtd.apps.CommentsXtdConfig"


def get_model():
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_MODEL)


def get_form():
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_FORM_CLASS)


VERSION = (2, 10, 7, "f", 0)  # following PEP 440


def get_version():
    version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"
    if VERSION[3] != "f":
        version = f"{version}{VERSION[3]}{VERSION[4]}"
    return version
