import os
import sys
from pathlib import Path


def pytest_configure(config):
    try:
        os.chdir("django_comments_xtd")
        sys.path.insert(0, f"{Path.cwd()}")
    except Exception:
        pass
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

    import django

    django.setup()
