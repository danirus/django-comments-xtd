# ruff: noqa: I001

VERSION = (3, 0, 0, "b", 0)  # following PEP 440


def get_model():
    """Returns the comment model class."""
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_MODEL)


def get_form():
    """Returns the comment ModelForm class."""
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_FORM_CLASS)


def get_form_target():
    """Returns the target URL for the comment form submission view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_FORM_TARGET)


def get_reaction_enum():
    """Returns the comment's reaction enum."""
    from django.utils.module_loading import import_string
    from django_comments_xtd.conf import settings

    return import_string(settings.COMMENTS_XTD_REACTION_ENUM)


def get_flag_url(comment):
    """Get the URL for the "flag this comment" view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_FLAG_URL, args=(comment.id,))


def get_delete_url(comment):
    """Get the URL for the "delete this comment" view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_DELETE_URL, args=(comment.id,))


def get_approve_url(comment):
    """Get the URL for the "approve this comment from moderation" view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_APPROVE_URL, args=(comment.id,))


def get_react_url(comment):
    """Get the URL for the "send feedback to this comment" view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_REACT_URL, args=(comment.id,))


def get_vote_url(comment):
    """Get the URL for the "vote on this comment" view."""
    from django.urls import reverse
    from django_comments_xtd.conf import settings

    return reverse(settings.COMMENTS_XTD_VOTE_URL, args=(comment.id,))


def get_version():
    version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"
    if VERSION[3] != "f":
        version = f"{version}{VERSION[3]}{VERSION[4]}"
    return version
