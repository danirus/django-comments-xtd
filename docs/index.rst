.. django-comments-xtd documentation master file, created by
   sphinx-quickstart on Mon Dec 19 19:20:12 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================   
django-comments-xtd
===================

.. module:: django_comments_xtd
   :synopsis: django-comments-extended.

.. highlightlang:: html+django

A Django pluggable application that can be used to add comments to your models. It extends the once official `Django Comments Framework <https://pypi.python.org/pypi/django-contrib-comments>`_ with the following features:

.. index::
   single: Features

1. Thread support, so comments can be nested.
2. Customizable maximum thread level, either for all models or on a per app.model basis.
3. Optional notifications on follow-up comments via email.
4. Mute links to allow cancellation of follow-up notifications.
5. Comment confirmation via email when users are not authenticated.
6. Comments hit the database only after they have been confirmed.
7. Registered users can like/dislike comments and can suggest comments removal.
8. Template tags to list/render the last N comments posted to any given list of app.model pairs.
9. Comments can be formatted in Markdown, reStructuredText, linebreaks or plain text.
10. Emails sent through threads (can be disable to allow other solutions, like a Celery app).

Contents
========
   
.. toctree::
   :maxdepth: 1

   quickstart
   tutorial
   example
   logic
   templatetags
   extending
   settings
   templates
