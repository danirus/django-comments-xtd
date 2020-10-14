django-comments-xtd |TravisCI|_
===================

.. |TravisCI| image:: https://secure.travis-ci.org/danirus/django-comments-xtd.png?branch=master
.. _TravisCI: https://travis-ci.org/danirus/django-comments-xtd

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
#. Fully functional JavaScript plugin using ReactJS, jQuery, Bootstrap, Remarkable and MD5.

Example sites and tests work under officially Django `supported versions <https://www.djangoproject.com/download/#supported-versions>`_:

* Django 3.1, 3.0, 2.2
* Python 3.8, 3.7, 3.6

Additional Dependencies:

* django-contrib-comments >=1.8
* djangorestframework >=3.9

Checkout the Docker image `danirus/django-comments-xtd-demo <https://hub.docker.com/r/danirus/django-comments-xtd-demo/>`_.

`Read The Docs <http://readthedocs.org/docs/django-comments-xtd/>`_.
