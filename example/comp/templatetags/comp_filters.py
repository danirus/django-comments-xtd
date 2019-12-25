# -*- coding: utf-8 -*-
from django.template import Library, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _

from django.conf import settings


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
