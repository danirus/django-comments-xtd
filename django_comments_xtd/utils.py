# Idea borrowed from Selwin Ong post:
# http://ui.co.id/blog/asynchronous-send_mail-in-django

import hashlib

try:
    import Queue as queue  # python2  # noqa: N813
except ImportError:
    import queue as queue  # python3  # noqa: PLC0414
import threading

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import salted_hmac

from django_comments_xtd.conf import settings
from django_comments_xtd.conf.defaults import COMMENTS_XTD_APP_MODEL_OPTIONS

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


def get_app_model_options(comment=None, content_type=None):
    """
    Get the app_model_option from `COMMENTS_XTD_APP_MODEL_OPTIONS`.

    If a comment is given, the content_type is extracted from it. Otherwise,
    the `content_type` kwarg has to be provided. The funcion checks whether
    there is a matching comments option's dictionary for the `app_label.model`
    for the `content_type` and returns it. Otherwise it returns the default
    from:

        `django_comments_xtd.conf.defaults.COMMENTS_XTD_APP_MODEL_OPTIONS`
    """
    defaults_options = dict.copy(COMMENTS_XTD_APP_MODEL_OPTIONS)
    settings_options = dict.copy(settings.COMMENTS_XTD_APP_MODEL_OPTIONS)
    if defaults_options != settings_options and "default" in settings_options:
        defaults_options["default"].update(settings_options.pop("default"))

    model_app_options = {}
    for app_model in settings_options:
        for k in defaults_options["default"]:
            if k not in settings_options[app_model]:
                model_app_options[k] = defaults_options["default"][k]
            else:
                model_app_options[k] = settings_options[app_model][k]

    if comment:
        content_type = ContentType.objects.get_for_model(comment.content_object)
        key = f"{content_type.app_label}.{content_type.model}"
    elif content_type:
        key = f"{content_type.app_label}.{content_type.model}"
    else:
        return defaults_options["default"]
    try:
        model_app_options.update(settings.COMMENTS_XTD_APP_MODEL_OPTIONS[key])
        return model_app_options
    except Exception:
        return model_app_options


def get_current_site_id(request=None):
    """it's a shortcut"""
    return getattr(get_current_site(request), "pk", 1)  # fallback value


def get_html_id_suffix(obj):
    value = f"{obj.__hash__()}"
    suffix = salted_hmac(settings.COMMENTS_XTD_SALT, value).hexdigest()
    return suffix


def get_user_avatar(comment):
    path = hashlib.md5(comment.user_email.lower().encode("utf-8")).hexdigest()
    param = urlencode({"s": 48})
    return f"//www.gravatar.com/avatar/{path}?{param}&d=identicon"
