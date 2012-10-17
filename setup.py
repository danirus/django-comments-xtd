from setuptools import setup, find_packages
from setuptools.command.test import test

def run_tests(*args):
    import subprocess
    subprocess.Popen(["python", "tests/runtests.py"]).wait()

test.run_tests = run_tests

setup(
    name = "django-comments-xtd",
    version = "1.1a1",
    packages = find_packages(),
    include_package_data = True,
    license = "MIT",
    description = "Django Comments Framework extension app with thread support, follow up notifications and email confirmations.",
    long_description = "A reusable Django app that extends the built-in Django's Comments Framework with thread support, following up notifications and comments that only hits the database after users confirm them by email.",
    author = "Daniel Rus Morales",
    author_email = "inbox@danir.us",
    maintainer = "Daniel Rus Morales",
    maintainer_email = "inbox@danir.us",
    url = "http://pypi.python.org/pypi/django-comments-xtd",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite = "dummy",
)
