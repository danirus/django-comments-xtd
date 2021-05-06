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
from django_comments_xtd.conf.defaults import COMMENTS_XTD_APP_MODEL_OPTIONS


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
    the content_type kwarg has to be provided. Checks whether there is a matching dictionary for the app_label.model of the content_type, and
    returns it. Otherwise it returns the default from:

        `django_comments_xtd.conf.defaults.COMMENTS_XTD_APP_MODEL_OPTIONS`.

    """
    defaults_options = COMMENTS_XTD_APP_MODEL_OPTIONS
    settings_options = settings.COMMENTS_XTD_APP_MODEL_OPTIONS
    model_app_options = {}
    if 'default' in settings_options:
        # The developer overwrite the default settings. Check whether
        # the developer added all the expected keys in the dictionary.
        has_missing_key = False
        for k in defaults_options['default'].keys():
            if k not in settings_options['default']:
                model_app_options[k] = defaults_options['default'][k]
            else:
                model_app_options[k] = settings_options['default'][k]

    if comment:
        content_type = ContentType.objects.get_for_model(comment.content_object)
        key = "%s.%s" % (content_type.app_label, content_type.model)
    elif content_type:
        key = content_type
    else:
        return defaults_options['default']
    try:
        model_app_options.update(settings.COMMENTS_XTD_APP_MODEL_OPTIONS[key])
        return model_app_options
    except Exception:
        return model_app_options


option_msgs = {
    'comment_flagging_enabled': {
        'PROD': "This type of comments are not allowed to be flagged.",
        'DEBUG': "Comments posted to instances of '%s.%s' are not "
                 "explicitly allowed to be flagged. Check the "
                 "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
    },
    'comment_reactions_enabled': {
        'PROD': "This type of comment are not allowed to receive reactions.",
        'DEBUG': "Comments posted to instances of '%s.%s' are not "
                 "explicitly allowed to receive reactions. Check the "
                 "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
    },
    'object_reactions_enabled': {
        'PROD': "This type of object are not allowed to receive reactions.",
        'DEBUG': "Instances of '%s.%s' are not explicitly allowed to receive "
                 "reactions. Check the COMMENTS_XTD_APP_MODEL_OPTIONS setting."
    }
}


def check_option(comment, option):
    ret_option = get_app_model_options(comment=comment)[option]
    if not ret_option:
        message = option_msgs[option]['PROD']
        if settings.DEBUG:
            ct = ContentType.objects.get_for_model(comment.content_object)
            message = option_msgs[option]['DEBUG'] % (ct.app_label, ct.model)
        raise PermissionDenied(detail=message, code=status.HTTP_403_FORBIDDEN)


def check_input_allowed(object):
    """
    This is a generic function called with the object being commented.
    It's defined as the default in 'COMMENTS_XTD_APP_MODEL_OPTIONS'.

    If you want to disallow comments input to your 'app.model' instances under
    a given conditions, rewrite this function in your code and modify the
    'COMMENTS_XTD_APP_MODEL_OPTIONS' in your settings.
    """
    return True


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
