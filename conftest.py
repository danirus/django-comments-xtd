import os
import sys


def pytest_configure(config):
    try:
        os.chdir("django_comments_xtd")
        sys.path.insert(0, os.getcwd())
    except:
        pass
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

    import django
    django.setup()
