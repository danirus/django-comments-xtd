# Idea borrowed from Selwin Ong post:
# http://ui.co.id/blog/asynchronous-send_mail-in-django

import hashlib
import queue
import threading

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http.response import HttpResponseRedirect
from django.utils.crypto import salted_hmac
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from django_comments_xtd.conf import settings
from django_comments_xtd.conf.defaults import COMMENTS_XTD_APP_MODEL_CONFIG

mail_sent_queue = queue.Queue()


# ruff:noqa: PLR0913
class EmailThread(threading.Thread):
    def __init__(
        self, subject, body, from_email, recipient_list, fail_silently, html
    ):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        _send_mail(
            self.subject,
            self.body,
            self.from_email,
            self.recipient_list,
            self.fail_silently,
            self.html,
        )
        mail_sent_queue.put(True)


def _send_mail(
    subject, body, from_email, recipient_list, fail_silently=False, html=None
):
    msg = EmailMultiAlternatives(subject, body, from_email, recipient_list)
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send(fail_silently)


def send_mail(
    subject, body, from_email, recipient_list, fail_silently=False, html=None
):
    if settings.COMMENTS_XTD_THREADED_EMAILS:
        EmailThread(
            subject, body, from_email, recipient_list, fail_silently, html
        ).start()
    else:
        _send_mail(
            subject, body, from_email, recipient_list, fail_silently, html
        )


# --------------------------------------------------------------------
def get_max_thread_level(content_type):
    """Get the max_thread_level for a given content_type."""
    app_model = f"{content_type.app_label}.{content_type.model}"
    return settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL.get(
        app_model, settings.COMMENTS_XTD_MAX_THREAD_LEVEL
    )


# --------------------------------------------------------------------
def get_app_model_options(comment=None, content_type=None):
    """
    Get the app_model_option from `COMMENTS_XTD_APP_MODEL_CONFIG`.

    If a comment is given, the content_type is extracted from it. Otherwise,
    the `content_type` kwarg has to be provided. The funcion checks whether
    there is a matching comments option's dictionary for the `app_label.model`
    for the `content_type` and returns it. Otherwise it returns the default
    from:

        `django_comments_xtd.conf.defaults.COMMENTS_XTD_APP_MODEL_CONFIG`
    """
    init_opts = dict.copy(COMMENTS_XTD_APP_MODEL_CONFIG)
    custom_opts = dict.copy(settings.COMMENTS_XTD_APP_MODEL_CONFIG)
    if init_opts != custom_opts and "default" in custom_opts:
        default_opts = dict.copy(init_opts["default"])
        default_opts.update(custom_opts["default"])
        init_opts["default"] = default_opts

    if comment:
        content_type = ContentType.objects.get_for_model(
            comment.content_object,
            for_concrete_model=settings.COMMENTS_XTD_FOR_CONCRETE_MODEL,
        )
        key = f"{content_type.app_label}.{content_type.model}"
    elif content_type:
        key = f"{content_type.app_label}.{content_type.model}"
    else:
        return init_opts["default"]

    try:
        model_app_opts = dict(init_opts["default"])
        model_app_opts.update(custom_opts[key])
        return model_app_opts
    except Exception:
        return init_opts["default"]


OPTION_MSGS = {
    "comments_flagging_enabled": {
        "PROD": "Comments not allowed to be flagged.",
        "DEBUG": (
            "Check the COMMENTS_XTD_APP_MODEL_CONFIG setting. "
            "Option 'comments_flagging_enabled' is False."
        ),
    },
    "comments_voting_enabled": {
        "PROD": "Comments not allowed to receive votes.",
        "DEBUG": (
            "Check the COMMENTS_XTD_APP_MODEL_CONFIG setting. "
            "Option 'comments_voting_enabled' is False."
        ),
    },
    "comments_reacting_enabled": {
        "PROD": "Comments not allowed to receive reactions.",
        "DEBUG": (
            "Check the COMMENTS_XTD_APP_MODEL_CONFIG setting. "
            "Option 'comments_reacting_enabled' is False."
        ),
    },
}


def check_option(option, comment=None, content_type=None, options=None):
    retrieved_option = False

    if options is not None:
        retrieved_option = options[option]
    else:
        retrieved_option = get_app_model_options(
            comment=comment, content_type=content_type
        )[option]

    if retrieved_option is False:
        env = "DEBUG" if settings.DEBUG else "PROD"
        raise PermissionDenied(
            detail=OPTION_MSGS[option][env], code=status.HTTP_403_FORBIDDEN
        )


def check_input_allowed(object):
    """
    This is a generic function called with the object being commented.
    It's defined as the default in 'COMMENTS_XTD_APP_MODEL_CONFIG'.

    If you want to disallow comments input to your 'app.model' instances under
    a given conditions, rewrite this function in your code and modify the
    'COMMENTS_XTD_APP_MODEL_CONFIG' in your settings.
    """
    return True


# --------------------------------------------------------------------
def get_current_site_id(request=None):
    """it's a shortcut"""
    return getattr(get_current_site(request), "pk", 1)  # fallback value


def get_html_id_suffix(obj):
    value = f"{obj.__hash__()}"
    suffix = salted_hmac(settings.COMMENTS_XTD_SALT, value).hexdigest()
    return suffix


def get_user_gravatar(comment):
    path = hashlib.md5(comment.user_email.lower().encode("utf-8")).hexdigest()
    param = urlencode({"s": 48})
    return f"//www.gravatar.com/avatar/{path}?{param}&d=identicon"


def redirect_to(comment):
    return HttpResponseRedirect(comment.get_absolute_url())
