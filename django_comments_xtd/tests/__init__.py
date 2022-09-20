import os
import sys


def setup_django_settings():  # pragma: no cover
    if os.environ.get("DJANGO_SETTINGS_MODULE", False):
        return
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.getcwd())
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"


def run_tests():  # pragma: no cover
    if not os.environ.get("DJANGO_SETTINGS_MODULE", False):
        setup_django_settings()

    import django
    from django.conf import settings
    from django.test.utils import get_runner

    django.setup()
    runner = get_runner(settings,
                        "django.test.runner.DiscoverRunner")
    test_suite = runner(verbosity=2, interactive=True, failfast=False)
    results = test_suite.run_tests(["django_comments_xtd"])
    return results
