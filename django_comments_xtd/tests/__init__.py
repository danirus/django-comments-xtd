import os
import sys


def setup_django_settings():
    if os.environ.get("DJANGO_SETTINGS_MODULE", False):
        return
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.getcwd())
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"


def run_tests():
    if not os.environ.get("DJANGO_SETTINGS_MODULE", False):
        setup_django_settings()

    import django
    from django.conf import settings
    from django.test.utils import get_runner

    # Django 1.7.x or above.
    if django.VERSION[0] >=1 or django.VERSION[1] >= 7:
        django.setup()
        runner = get_runner(settings,
                            "django.test.runner.DiscoverRunner")
    else:
        runner = get_runner(settings,
                            "django.test.simple.DjangoTestSuiteRunner")
    test_suite = runner(verbosity=2, interactive=True, failfast=False)
    results = test_suite.run_tests(["django_comments_xtd"])
    return results
