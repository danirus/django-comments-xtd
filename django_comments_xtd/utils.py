# Idea borrowed from Selwin Ong post:
# http://ui.co.id/blog/asynchronous-send_mail-in-django

import hashlib
import queue as queue
import threading
from urllib.parse import urlencode

from django.core.mail import EmailMultiAlternatives
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponseRedirect
from django.utils.crypto import salted_hmac

from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from django_comments_xtd import get_model
from django_comments_xtd.conf import settings
from django_comments_xtd.conf.defaults import (
    COMMENTS_XTD_APP_MODEL_OPTIONS, COMMENTS_XTD_REACTIONS_JS_OVERLAYS)
from django_comments_xtd.paginator import CommentsPaginator


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
    the content_type kwarg has to be provided. Checks whether there is a
    matching dictionary for the app_label.model of the content_type, and
    returns it. Otherwise it returns the default from:

        `django_comments_xtd.conf.defaults.COMMENTS_XTD_APP_MODEL_OPTIONS`.

    """
    defaults_options = dict.copy(COMMENTS_XTD_APP_MODEL_OPTIONS)
    settings_options = dict.copy(settings.COMMENTS_XTD_APP_MODEL_OPTIONS)
    if defaults_options != settings_options and 'default' in settings_options:
        defaults_options['default'].update(settings_options.pop('default'))

    model_app_options = {}
    for app_model in settings_options.keys():
        for k in defaults_options['default'].keys():
            if k not in settings_options[app_model]:
                model_app_options[k] = defaults_options['default'][k]
            else:
                model_app_options[k] = settings_options[app_model][k]

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
def get_reactions_js_overlays(comment=None, content_type=None):
    """
    Get the app_model_option from COMMENTS_XTD_REACTIONS_JS_OVERLAYS.

    If a comment is given, the content_type is extracted from it. Otherwise,
    the content_type kwarg has to be provided. Checks whether there is a
    matching dictionary for the app_label.model of the content_type, and
    returns it. Otherwise it returns the default from:

        `django_comments_xtd.conf.defaults.COMMENTS_XTD_REACTIONS_JS_OVERLAYS`.

    """
    _defaults = dict.copy(COMMENTS_XTD_REACTIONS_JS_OVERLAYS)
    _settings = dict.copy(settings.COMMENTS_XTD_REACTIONS_JS_OVERLAYS)
    if _defaults != _settings and 'default' in _settings:
        _defaults['default'].update(_settings.pop('default'))

    _for_app_model = {}
    for app_model in _settings.keys():
        for k in _defaults['default'].keys():
            if k not in _settings[app_model]:
                _for_app_model[k] = _defaults['default'][k]
            else:
                _for_app_model[k] = _settings[app_model][k]

    if comment:
        content_type = ContentType.objects.get_for_model(comment.content_object)
        key = "%s.%s" % (content_type.app_label, content_type.model)
    elif content_type:
        key = content_type
    else:
        return _defaults['default']
    try:
        _for_app_model.update(settings.COMMENTS_XTD_REACTIONS_JS_OVERLAYS[key])
        return _for_app_model
    except Exception:
        return _for_app_model


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


def redirect_to(comment, request=None, page_number=None):
    cm_abs_url = comment.get_absolute_url()
    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.GET.get(cpage_qs_param, None) if request else page_number
    if cpage:
        hash_pos = cm_abs_url.find("#")
        cm_anchor = cm_abs_url[hash_pos:]
        cm_abs_url = cm_abs_url[:hash_pos]
        url = f"{cm_abs_url}?{cpage_qs_param}={cpage}{cm_anchor}"
        return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(cm_abs_url)


def get_comment_page_number(request, content_type_id, object_id, comment_id):
    """
    Returns the page number in which the `comment_id` is listed.
    """
    num_orphans = settings.COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS
    page_size = settings.COMMENTS_XTD_ITEMS_PER_PAGE
    if page_size == 0:
        return 1  # Pagination is disabled.

    # Replicate the logic in django_comments/templatetags/comments.py,
    # BaseCommentNode.get_queryset method.

    site_id = getattr(settings, "SITE_ID", None)
    if not site_id:
        site_id = get_current_site_id(request)

    qs = get_model().objects.filter(
        content_type_id=content_type_id,
        object_pk=object_id,
        site__pk=site_id)

    # The is_public and is_removed fields are implementation details of the
    # built-in comment model's spam filtering system, so they might not
    # be present on a custom comment model subclass. If they exist, we
    # should filter on them.
    field_names = [f.name for f in get_model()._meta.fields]
    if 'is_public' in field_names:
        qs = qs.filter(is_public=True)
    if (
        getattr(settings, 'COMMENTS_HIDE_REMOVED', True)
        and 'is_removed' in field_names
    ):
        qs = qs.filter(is_removed=False)

    if 'user' in field_names:
        qs = qs.select_related('user')

    comment_id = int(comment_id)
    paginator = CommentsPaginator(qs, page_size, orphans=num_orphans)
    for page_number in range(1, paginator.num_pages + 1):
        page = paginator.page(page_number)
        if comment_id in [cm.id for cm in page.object_list]:
            return page_number
    raise Exception("Comment %d not listed in any page." % comment_id)
