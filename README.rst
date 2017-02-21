django-comments-xtd |TravisCI|_
===================

.. |TravisCI| image:: https://secure.travis-ci.org/danirus/django-comments-xtd.png?branch=master
.. _TravisCI: https://travis-ci.org/danirus/django-comments-xtd

Demo site and tests working under officially Django `supported versions <https://www.djangoproject.com/download/#supported-versions>`_:

* Django 1.8, Django 1.9 and Django 1.10
* Python 2.7 and Python 3 (3.2, 3.4, 3.5, 3.6)

A reusable django app that extends the `django-contrib-comments <https://pypi.python.org/pypi/django-contrib-comments>`_ framework with:

#. Thread support, so comments may be nested.
#. The maximum thread level can be set up either for all models or on a per app.model basis.
#. Optional notification of follow-up comments via email.
#. Mute links on follow-up emails to allow follow-up notification cancellation.
#. Comment confirmation via email when users are not authenticated.
#. Comments hit the database only when have been confirmed.
#. Registered users can like/dislike comments and can suggest comments removal.
#. Template tags to list/render the last N comments posted to any given list of app.model pairs.
#. Comments can be formatted in Markdown, reStructuredText, linebreaks or plain text.
#. Emails sent through threads (can be disable to allow other solutions, like a Celery app).


Tutorial
--------

Read the tutorial covering every feature in the documentation at:

* `Read The Docs`_
* `Python Packages Site`_

.. _`Read The Docs`: http://readthedocs.org/docs/django-comments-xtd/
.. _`Python Packages Site`: http://packages.python.org/django-comments-xtd/


Demo projects
-------------

Includes several demo sites and an extensive test suite.

Check out the demo projects coming with the package:

#. **simple**: Single model with **non-threaded** comments.
#. **simple_threads**: Single model with **threaded** comments up to level 2.
#. **multiple**: Several models with comments, and a maximum thread level defined on per app.model basis.
#. **custom_comments**: How to extend django-comments-xtd with your own comment model and form.


Contributions
-------------
   
If you commit code, please consider adding proper coverage (especially if it has a chance for a regression) in the test suite. Run the tests with the ``python setup.py test`` command.
