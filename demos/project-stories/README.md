# Project Stories

It is a Django project with a few dependencies:
 * django>=4,<5
 * django-contrib-comments>=2.1,<2.2
 * django-comments-xtd>=3.0,<4
 * djangorestframework>=3.12,<3.13
 * django-avatar>=5.0,<5.1

Features:
 * It is a project using Python and Django in the backend, and vanilla JavaScript in the frontend.
 * Users and visitors can send comments and replies.
 * Comments can be nested two levels.
 * Templates are customized to display users' avatars in comments.

## Install

Create a virtual environment:

    $ python3.9 -m venv psenv
    $ source psenv/bin/activate
    $ pip install -r requirements.txt

### Install django-comments-xtd

Install django-comments-xtd passing the path back to the root of the package (where pip can find the setup.py):

    $ pip install -e ../..

