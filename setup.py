import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


def run_tests(*args):
    from django_comments_xtd.tests import run_tests
    errors = run_tests()
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


test.run_tests = run_tests


setup(
    name="django-comments-xtd",
    version="2.9.12",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description=("Django Comments Framework extension app with thread "
                 "support, follow up notifications and email "
                 "confirmations."),
    long_description=("A reusable Django app that extends django-contrib-"
                      "comments Framework with thread support, following up "
                      "notifications and comments that only hits the "
                      "database after users confirm them by email."),
    author="Daniela Rus Morales",
    author_email="danirus@eml.cc",
    maintainer="Daniela Rus Morales",
    maintainer_email="danirus@eml.cc",
    url="http://pypi.python.org/pypi/django-comments-xtd",
    install_requires=[
        'Django>=3,<5.1',
        'django-contrib-comments>=2.2,<2.3',
        'djangorestframework>=3.12,<3.15',
        'docutils',
        'six',
        'pytz',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
    test_suite="dummy",
    zip_safe=True
)
