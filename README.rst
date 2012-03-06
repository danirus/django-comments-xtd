Django-comments-xtd
===================

By Daniel Rus Morales <http://danir.us/>

* http://pypi.python.org/pypi/django-comments-xtd/
* http://github.com/danirus/django-comments-xtd/

A reusable Django app that extends the built-in Django's Comments Framework with:

1. Optional notification of follow-up comments via email
2. Comment confirmation via email when users are not authenticated
3. Comments hit the database only when have been confirmed
4. Template tags to list/render the last N comments posted to any list of models
5. Comments formatted in Markdown, reStructuredText, linebreaks or plain text

Read the documentation at:

* `Read The Docs`_
* `Python Packages Site`_

.. _`Read The Docs`: http://readthedocs.org/docs/django-comments-xtd/
.. _`Python Packages Site`: http://packages.python.org/django-comments-xtd/

Includes two **demo sites** and a limited **test suite**. If you commit code, please consider adding proper coverage (especially if it has a chance for a regression) in the test suite.

Run the tests with:  ``python setup.py test``
