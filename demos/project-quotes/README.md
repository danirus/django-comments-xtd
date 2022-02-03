# Project Quotes

It is a very simple project with only three dependencies:
 * django>=4,<5
 * django-contrib-comments>=2.1,<2.2
 * django-comments-xtd

Features:
 * It is a fully backend driven project (no JavaScript needed).
 * Users and visitors can send comments and replies.
 * Comments can be nested one level.

## Install

Create a virtual environment:

    $ python3.9 -m venv pqenv
    $ source pqenv/bin/activate
    $ pip install -r requirements.txt

### Install django-comments-xtd

Install django-comments-xtd passing the path back to the root of the package (where pip can find the setup.py):

    $ pip install -e ../..

### Setup the Django project

Run Django's `migrate` command and load the fixture data:

    $ cd project_quotes
    $ python manage.py migrate
    $ python manage.py loaddata ../fixtures/sites.json
    $ python manage.py loaddata ../fixtures/users.json
    $ python manage.py loaddata ../fixtures/quotes.json
    $ python manage.py loaddata ../fixtures/comments.json

And finally launch the development server:

    $ python manage.py runserver localhost:4048
