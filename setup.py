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


readme = ""
with open("README.rst", "r") as readme_file:
    readme = readme_file.read()


requirements = []
with open("requirements.txt", "r") as req_file:
    for item in req_file:
        requirements.append(item)


setup(
    name="django-comments-xtd",
    version="3.0.0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description=("Django comments framework extension app with thread "
                 "support, follow up notifications and email "
                 "confirmations."),
    long_description=readme,
    long_description_content_type="text/x-rst",
    author="Daniel Rus Morales",
    author_email="mbox@danir.us",
    maintainer="Daniel Rus Morales",
    maintainer_email="mbox@danir.us",
    url="http://pypi.python.org/pypi/django-comments-xtd",
    install_requires=requirements,
    setup_requires=['wheel'],
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
