from django.conf import settings as django_settings
from django.utils.functional import LazyObject

from django_comments_xtd.conf import defaults as app_settings


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(app_settings, django_settings)


class Settings:
    def __init__(self, *args):
        for item in args:
            for attr in dir(item):
                if attr == attr.upper():
                    setattr(self, attr, getattr(item, attr))


settings = LazySettings()
