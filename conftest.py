import os
import sys
from pathlib import Path

plugins = [
    "django_comments_xtd.tests.pytest_fixtures",
]


def pytest_configure(config):
    try:
        os.chdir("django_comments_xtd")
        sys.path.insert(0, f"{Path.cwd()}")
    except Exception:
        pass
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

    import django

    django.setup()

    # -------------------------------------
    # Load fixtures listed in 'my_plugins'.

    for plugin_module in plugins:
        config.pluginmanager.import_plugin(plugin_module)
