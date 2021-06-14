import os
import sys


def setup_django_settings():
    os.chdir("django_comments_xtd")
    sys.path.insert(0, os.getcwd())
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"


def pytest_configure(config):
    if not os.environ.get("DJANGO_SETTINGS_MODULE", False):
        setup_django_settings()

    import django
    django.setup()
