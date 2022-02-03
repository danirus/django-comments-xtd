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

### Setup the Django project

Run Django's `migrate` command and load the fixture data:

    $ cd project_quotes
    $ python manage.py migrate
    $ python manage.py loaddata ../fixtures/sites.json
    $ python manage.py loaddata ../fixtures/users.json
    $ python manage.py loaddata ../fixtures/stories.json
    $ python manage.py loaddata ../fixtures/comments.json

And finally launch the development server:

    $ python manage.py runserver localhost:4050

### Users

The project allows you to login using any of the users provided with the `users.json` fixture. Here are their login email and their password:

 * `admin@example.com`, password `admin`
 * `fulanito@example.com`, password `fulanito`
 * `mengo@example.com`, password `mengo`
 * `daniela.rushmore@example.com`, password `daniela.rushmore`
 * `lena.rosenthal@example.com`, password `lena.rosenthal`
 * `amalia.ocean@example.com`, password `amalia.ocean`
 * `isabel.azul@example.com`, password `isabel.azul`
 * `joe.bloggs@example.com`, password `joe.bloggs`
 * `eva.rizzi@example.com`, password `eva.rizzi`
 * `david.fields@example.com`, password `david.fields`

