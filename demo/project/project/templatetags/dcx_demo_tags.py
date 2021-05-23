import hashlib
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import Http404
from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from avatar.templatetags.avatar_tags import avatar
from avatar.utils import cache_result


register = Library()


lang_names = {
    'de': _('German'),
    'en': _('English'),
    'es': _('Spanish'),
    'fi': _('Finnish'),
    'fr': _('French'),
    'hu': _('Hungarian'),
    'it': _('Italian'),
    'nl': _('Dutch'),
    'no': _('Norwegian'),
    'pl': _('Polish'),
    'pt': _('Portuguese'),
    'ru': _('Russian'),
    'tr': _('Turkish'),
    'uk': _('Ukrainian'),
    'zh': _('Chinese'),
}


lang_orig_names = {
    'de': 'Deutsch',
    'en': 'English',
    'es': 'español',
    'fi': 'suomi',
    'fr': 'français',
    'hu': 'magyar',
    'it': 'italiano',
    'nl': 'Nederlands',
    'no': 'Norsk',
    'pl': 'polski',
    'pt': 'português',
    'ru': 'русский',
    'tr': 'Türkçe',
    'uk': 'українська',
    'zh': '中文',
}


@register.filter
def language_name(value):
    try:
        return lang_orig_names[value]
    except KeyError:
        return value
language_name.is_safe = True


@register.filter
def language_tuple(value):
    try:
        return "%s, %s" % (lang_orig_names[value], lang_names[value])
    except KeyError:
        return value
language_tuple.is_safe = True


def get_gravatar_url(email, size=48, avatar='identicon'):
    """
    This is the parameter of the production avatar.
    The first parameter is the way of generating the
    avatar and the second one is the size.
    The way os generating has mp/identicon/monsterid/wavatar/retro/hide.
    """
    return ("//www.gravatar.com/avatar/%s?%s&d=%s" %
            (hashlib.md5(email.lower().encode('utf-8')).hexdigest(),
             urlencode({'s': str(size)}), avatar))


@cache_result
@register.simple_tag
def get_user_avatar_or_gravatar(email, config='48,identicon'):
    size, gravatar_type = config.split(',')
    try:
        size_number = int(size)
    except ValueError:
        raise Http404(_('The given size is not a number: %s' % repr(size)))

    try:
        user = get_user_model().objects.get(email=email)
        return avatar(user, size_number)
    except get_user_model().DoesNotExist:
        url = get_gravatar_url(email, size_number, gravatar_type)
        return mark_safe('<img src="%s" height="%d" width="%d">' %
                        (url, size_number, size_number))
