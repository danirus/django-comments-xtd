# ruff:noqa: I001, PLC0415

default_app_config = "django_comments_xtd.apps.CommentsXtdConfig"


def get_model():
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_MODEL)


def get_form():
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_FORM_CLASS)


def get_form_target():
    from django.urls import reverse

    return reverse("comments-xtd-post")


def get_reaction_enum():
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_REACTION_ENUM)


VERSION = (3, 0, 0, "b", 0)  # following PEP 440


def get_version():
    version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"
    if VERSION[3] != "f":
        version = f"{version}{VERSION[3]}{VERSION[4]}"
    return version
