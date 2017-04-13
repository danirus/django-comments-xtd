django-comments-xtd |TravisCI|_
===================

.. |TravisCI| image:: https://secure.travis-ci.org/danirus/django-comments-xtd.png?branch=master
.. _TravisCI: https://travis-ci.org/danirus/django-comments-xtd

Demo site and tests working under officially Django `supported versions <https://www.djangoproject.com/download/#supported-versions>`_:

* Django 1.8, 1.9, 1.10 and 1.11
* Python 2.7, 3.2, 3.4, 3.5, 3.6

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

Includes 3 example projects:

#. **simple**: Single model with comments.
#. **custom**: Showcase how to extend django-comments-xtd with your own comment model and form.
#. **comp**: Several models with comments, different nesting levels for each model, removal suggestion flags, like and dislike buttons, list of users who liked/disliked comments, etc.


Contributions
-------------
   
If you commit code, please consider adding proper coverage (especially if it has a chance for a regression) in the test suite. Run the tests with the ``python setup.py test`` command. Check full compatibility with supported versions by running ``tox``.
