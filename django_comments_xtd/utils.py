# Idea borrowed from Selwin Ong post:
# http://ui.co.id/blog/asynchronous-send_mail-in-django

from copy import copy
import hashlib
import queue as queue
import threading
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.core.mail import EmailMultiAlternatives
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import salted_hmac

from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from django_comments_xtd.conf import settings


mail_sent_queue = queue.Queue()


class EmailThread(threading.Thread):
    def __init__(self, subject, body, from_email, recipient_list,
                 fail_silently, html):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        _send_mail(self.subject, self.body, self.from_email,
                   self.recipient_list, self.fail_silently, self.html)
        mail_sent_queue.put(True)


def _send_mail(subject, body, from_email, recipient_list,
               fail_silently=False, html=None):
    msg = EmailMultiAlternatives(subject, body, from_email, recipient_list)
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send(fail_silently)


def send_mail(subject, body, from_email, recipient_list,
              fail_silently=False, html=None):
    if settings.COMMENTS_XTD_THREADED_EMAILS:
        EmailThread(subject, body, from_email, recipient_list,
                    fail_silently, html).start()
    else:
        _send_mail(subject, body, from_email, recipient_list,
                   fail_silently, html)


# --------------------------------------------------------------------
def get_app_model_options(comment=None, content_type=None):
    """
    Get the app_model_option from COMMENTS_XTD_APP_MODEL_OPTIONS.

    If a comment is given, the content_type is extracted from it. Otherwise,
    the content_type kwarg has to be provided. The funcion checks whether there
    is a matching dictionary for the app_label.model of the content_type, and
    returns it. Otherwise it returns the default from:
        `django_comments_xtd.defaults.COMMENTS_XTD_APP_MODEL_OPTIONS`.
    """
    default = {
        'who_can_post': 'all',  # Valid values: "users", "all"
        'allow_comment_flagging': False,
        'allow_comment_reactions': False,
        'allow_object_reactions': False
    }
    if 'default' in settings.COMMENTS_XTD_APP_MODEL_OPTIONS:
        # The developer overwrite the default settings. Check whether
        # the developer added all the expected keys in the dictionary.
        has_missing_key = False
        for k in default.keys():
            if k not in settings.COMMENTS_XTD_APP_MODEL_OPTIONS['default']:
                has_missing_key = True
        if not has_missing_key:
            default = copy(settings.COMMENTS_XTD_APP_MODEL_OPTIONS['default'])

    if comment:
        content_type = ContentType.objects.get_for_model(comment.content_object)
        key = "%s.%s" % (content_type.app_label, content_type.model)
    elif content_type:
        key = content_type
    else:
        return default
    try:
        default.update(settings.COMMENTS_XTD_APP_MODEL_OPTIONS[key])
        return default
    except Exception:
        return default


option_msgs = {
    'allow_flagging': {
        'PROD': "This typo of comments are not allowed to be flagged.",
        'DEBUG': "Comments posted to instances of '%s.%s' are not "
                 "explicitly allowed to be flagged. Check the "
                 "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
    },
    'allow_reactions': {
        'PROD': "This typo of comment are not allowed to receive reactions.",
        'DEBUG': "Comments posted to instances of '%s.%s' are not "
                 "explicitly allowed to receive reactions. Check the "
                 "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
    }
}


def check_option(comment, option):
    is_allowed = get_app_model_options(comment=comment)[option]
    if not is_allowed:
        message = option_msgs[option]['PROD']
        if settings.DEBUG:
            ct = ContentType.objects.get_for_model(comment.content_object)
            message = option_msgs[option]['DEBUG'] % (ct.app_label, ct.model)
        raise PermissionDenied(detail=message, code=status.HTTP_403_FORBIDDEN)


# --------------------------------------------------------------------
def get_current_site_id(request=None):
    """ it's a shortcut """
    return getattr(get_current_site(request), 'pk', 1)  # fallback value


def get_html_id_suffix(object):
    value = "%s" % object.__hash__()
    suffix = salted_hmac(settings.COMMENTS_XTD_SALT, value).hexdigest()
    return suffix


def get_user_avatar(comment):
    path = hashlib.md5(comment.user_email.lower().encode('utf-8')).hexdigest()
    param = urlencode({'s': 48})
    return "//www.gravatar.com/avatar/%s?%s&d=identicon" % (path, param)
