# django-comments-xtd  [![tests](https://github.com/danirus/django-comments-xtd/workflows/tests/badge.svg)](https://github.com/danirus/django-comments-xtd/actions/workflows/ci-pipeline.yml)

Work on version 3.0 is taking place in the `main` branch. When curious, take a look at the example `mockups_project`. Still some points `TODO.md` to have it ready. 🚀

A Django pluggable application that adds comments to your project.

<p align="center"><img align="center" src="https://github.com/danirus/django-comments-xtd/raw/main/docs/images/cover-gh.png"></p>

It extends the original [Django Comments Framework](https://pypi.python.org/pypi/django-contrib-comments) with the following features:

* Thread support, so comments can be nested.
* Customizable maximum thread level on per `app.model` basis.
* Optional notifications on follow-up comments via email.
* Mute links to allow cancellation of follow-up notifications.
* Comment confirmation via email when users are not authenticated.
* Comments hit the database only after they have been confirmed.
* Enable comment reactions, comment votes and comment flagging on per `app.model` basis.
* Comment reactions visitors can choose are customizable. Defaults to thumb up and thumb down.
* Several themes available.
* Plain vanilla JavaScript plugin.
* ReST API to support your own frontend.
* ...

Example sites and tests run under officially Django [supported versions](https://www.djangoproject.com/download/#supported-versions):

* Django 6.0, 5.1, 5.0, 4.2
* Python 3.14, 3.13, 3.12, 3.11

Additional Dependencies:

* django-contrib-comments >=2.2
* djangorestframework >=3.12,<3.17

Check out the tutorial and examples in the [documentation](http://readthedocs.org/docs/django-comments-xtd/).
