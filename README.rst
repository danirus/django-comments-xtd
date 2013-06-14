django-comments-xtd
===================

|TravisCI|_

.. |TravisCI| image:: https://secure.travis-ci.org/danirus/django-comments-xtd.png?branch=master
.. _TravisCI: https://travis-ci.org/danirus/django-comments-xtd

Tested under:

* Python 3.2 and django 1.5.1: `builds <http://buildbot.danir.us/builders/django-comments-xtd-py32dj15>`_
* Python 2.7 and django 1.5.1: `builds <http://buildbot.danir.us/builders/django-comments-xtd-py27dj15>`_
* Python 2.7 and django 1.4.5: `builds <http://buildbot.danir.us/builders/django-comments-xtd-py27dj14>`_

By Daniel Rus Morales <http://danir.us/>

* http://pypi.python.org/pypi/django-comments-xtd/
* http://github.com/danirus/django-comments-xtd/

A reusable django app that extends the built-in django's comments framework with:

1. Thread support, so comments may be nested
2. The maximum thread level can be set up either for all models or on a per app.model basis
3. Optional notification of follow-up comments via email
4. Comment confirmation via email when users are not authenticated
5. Comments hit the database only when have been confirmed
6. Template tags to list/render the last N comments posted to any list of models
7. Comments formatted in Markdown, reStructuredText, linebreaks or plain text
8. All emails are sent in threads apart to avoid response blocking

Read the documentation at:

* `Read The Docs`_
* `Python Packages Site`_

.. _`Read The Docs`: http://readthedocs.org/docs/django-comments-xtd/
.. _`Python Packages Site`: http://packages.python.org/django-comments-xtd/

Includes three **demo sites** and a limited **test suite**. If you commit code, please consider adding proper coverage (especially if it has a chance for a regression) in the test suite.

Run the tests with:  ``python setup.py test``

And see the live demos:

1. `simple <http://demos.danir.us/django-comments-xtd/simple/>`_: Single model with **non-threaded** comments
2. `simple_threads <http://demos.danir.us/django-comments-xtd/simple-threads/>`_: Single model with **threaded** comments up to level 2
3. `multiple <http://demos.danir.us/django-comments-xtd/multiple/>`_: Several models with comments, and a maximum thread level defined on per app.model basis.

Admin access with user **admin**, password **admin**. DBs cleared every 30 minutes.
