.. django-comments-xtd documentation master file, created by
   sphinx-quickstart on Mon Dec 19 19:20:12 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
Welcome to django-comments-xtd
==============================

.. module:: django_comments_xtd
   :synopsis: django-comments-extended.

.. highlightlang:: html+django

A Django pluggable application that adds comments to your project. It extends
the once official `Django Comments Framework
<https://pypi.python.org/pypi/django-contrib-comments>`_.


.. note::

    This documentation represents the current version, v2.7.0, of
    django-comments-xtd. For old versions of the documentation:

    * v2.6.2: https://django-comments-xtd.readthedocs.io/en/2.6.2/
    * v2.5.1: https://django-comments-xtd.readthedocs.io/en/2.5.1/
    * v2.4.3: https://django-comments-xtd.readthedocs.io/en/2.4.3/
    * v2.3.1: https://django-comments-xtd.readthedocs.io/en/2.3.1/
    * v2.2.1: https://django-comments-xtd.readthedocs.io/en/2.2.1/
    * v2.1.0: https://django-comments-xtd.readthedocs.io/en/2.1.0/
    * v2.0.10: https://django-comments-xtd.readthedocs.io/en/2.0.10/
    * v1.7.1: https://django-comments-xtd.readthedocs.io/en/1.7.1/
    * v1.6.7: https://django-comments-xtd.readthedocs.io/en/1.6.7/
    * v1.5.1: https://django-comments-xtd.readthedocs.io/en/1.5.1/


Features
========

.. index::
   single: Features

#. Thread support, so comments can be nested.
#. Customizable maximum thread level, either for all models or on a per
   app.model basis.
#. Optional notifications on follow-up comments via email.
#. Mute links to allow cancellation of follow-up notifications.
#. Comment confirmation via email when users are not authenticated.
#. Comments hit the database only after they have been confirmed.
#. Registered users can like/dislike comments and can suggest comments removal.
#. Template tags to list/render the last N comments posted to any given list of
   app.model pairs.
#. Emails sent through threads (can be disable to allow other solutions, like a
   Celery app).
#. Fully functional JavaScript plugin using ReactJS, jQuery, Bootstrap,
   Remarkable and MD5.

.. image:: images/cover.png

Getting started
===============

Start with these documents to get you up and running:

.. toctree::
   :maxdepth: 2

   quickstart
   tutorial
   example


Advanced Use
============

Once you've got django-comments-xtd working, you may want to know more about
specific features, or check out the use cases to see how others customize it.
   
.. toctree::
   :maxdepth: 1

   logic
   webapi
   javascript
   templatetags
   migrating
   extending
   i18n
   settings
   templates
   usecases
