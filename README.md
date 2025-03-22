# django-comments-xtd  [![tests](https://github.com/danirus/django-comments-xtd/workflows/tests/badge.svg)](https://github.com/danirus/django-comments-xtd/actions/workflows/ci-pipeline.yml)

A Django pluggable application that adds comments to your project.

<p align="center"><img align="center" src="https://github.com/danirus/django-comments-xtd/blob/master/docs/images/cover.light.png"></p>

It extends the original [Django Comments Framework](https://pypi.python.org/pypi/django-contrib-comments) with the following features:

* Thread support, so comments can be nested.
* Customizable maximum thread level, either for all models or on a per app.model basis.
* Optional notifications on follow-up comments via email.
* Mute links to allow cancellation of follow-up notifications.
* Comment confirmation via email when users are not authenticated.
* Comments hit the database only after they have been confirmed.
* Registered users can like/dislike comments and can suggest comments removal.
* Template tags to list/render the last N comments posted to any given list of app.model pairs.
* Emails sent through threads (can be disable to allow other solutions, like a Celery app).
* Fully functional JavaScript plugin using ReactJS, Bootstrap 5.3 and Remarkable.

Example sites and tests run under officially Django [supported versions](https://www.djangoproject.com/download/#supported-versions):

* Django 5.1, 5.0, 4.2, 4.1
* Python 3.13, 3.12, 3.11, 3.10

Additional Dependencies:

* django-contrib-comments >=2.2
* djangorestframework >=3.12,<3.16

Check out the tutorial and examples in the [documentation](http://readthedocs.org/docs/django-comments-xtd/).
