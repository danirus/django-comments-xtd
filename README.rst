django-comments-xtd
===================

Major version v1 is the latest to cover support from Django 1.4 to Django 1.9. Next major version v2.0 will only support officially maintained versions of Django.
      
|TravisCI|_

.. |TravisCI| image:: https://secure.travis-ci.org/danirus/django-comments-xtd.png?branch=master
.. _TravisCI: https://travis-ci.org/danirus/django-comments-xtd

Tested under:

* Python 3.5 and django 1.9
* Python 3.4 and django 1.8.7
* Python 3.4 and django 1.7.11
* Python 2.7 and django 1.7.11
* Python 2.7 and django 1.4.20

By Daniel Rus Morales <http://danir.us/>

* http://pypi.python.org/pypi/django-comments-xtd/
* http://github.com/danirus/django-comments-xtd/

A reusable django app that extends the `django-contrib-comments <https://pypi.python.org/pypi/django-contrib-comments>`_ framework with:

1. Thread support, so comments may be nested
2. The maximum thread level can be set up either for all models or on a per app.model basis
3. Optional notification of follow-up comments via email
4. Mute links on follow-up emails to allow follow-up notification cancellation
5. Comment confirmation via email when users are not authenticated
6. Comments hit the database only when have been confirmed
7. Template tags to list/render the last N comments posted to any given list of app.model pairs
8. Comments can be formatted in Markdown, reStructuredText, linebreaks or plain text
9. Emails sent through threads (can be disable to allow other solutions, like a Celery app)

Read the documentation at:

* `Read The Docs`_
* `Python Packages Site`_

.. _`Read The Docs`: http://readthedocs.org/docs/django-comments-xtd/
.. _`Python Packages Site`: http://packages.python.org/django-comments-xtd/

Includes three **demo sites** and a limited **test suite**. If you commit code, please consider adding proper coverage (especially if it has a chance for a regression) in the test suite.

Run the tests with:  ``python setup.py test``

Check out the demo projects coming with the package:

1. **simple**: Single model with **non-threaded** comments
2. **simple_threads**: Single model with **threaded** comments up to level 2
3. **multiple**: Several models with comments, and a maximum thread level defined on per app.model basis.
