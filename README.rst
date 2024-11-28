django-comments-xtd |gha-tests-badge|
=====================================

.. |gha-tests-badge| image:: https://github.com/danirus/django-comments-xtd/workflows/tests/badge.svg
.. _gha-tests-badge: https://github.com/danirus/django-comments-xtd/actions/workflows/ci-pipeline.yml

A Django pluggable application that adds comments to your project.

.. image:: https://github.com/danirus/django-comments-xtd/blob/master/docs/images/cover.png

It extends the once official `django-contrib-comments <https://pypi.python.org/pypi/django-contrib-comments>`_ with the following features:

#. Thread support, so comments can be nested.
#. Customizable maximum thread level, either for all models or on a per app.model basis.
#. Optional notifications on follow-up comments via email.
#. Mute links to allow cancellation of follow-up notifications.
#. Comment confirmation via email when users are not authenticated.
#. Comments hit the database only after they have been confirmed.
#. Registered users can like/dislike comments and can suggest comments removal.
#. Template tags to list/render the last N comments posted to any given list of app.model pairs.
#. Emails sent through threads (can be disable to allow other solutions, like a Celery app).
#. Fully functional JavaScript plugin using ReactJS, Bootstrap 5.3 and Remarkable.

Example sites and tests work under officially Django `supported versions <https://www.djangoproject.com/download/#supported-versions>`_:

* Django 5.1, 5.0, 4.2, 4.1
* Python 3.13, 3.12, 3.11, 3.10

Additional Dependencies:

* django-contrib-comments >=2.2
* djangorestframework >=3.12,<3.16

Checkout the Docker image `danirus/django-comments-xtd-demo <https://hub.docker.com/r/danirus/django-comments-xtd-demo/>`_.

`Read The Docs <http://readthedocs.org/docs/django-comments-xtd/>`_.
