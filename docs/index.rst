.. django-comments-xtd documentation master file, created by
   sphinx-quickstart on Mon Dec 19 19:20:12 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

**django-comments-xtd** extends the built-in Django's Comments Framework with:

.. index::
   single: Features

1. Thread support, so comments may be nested
2. The maximum thread level can be set up either for all models or on a per app.model basis
3. Optional notification of follow-up comments via email
4. Mute links on follow-up emails to allow follow-up notification cancellation
5. Comment confirmation via email when users are not authenticated
6. Comments hit the database only when have been confirmed
7. Template tags to list/render the last N comments posted to any given list of app.model pairs
8. Comments can be formatted in Markdown, reStructuredText, linebreaks or plain text
9. Emails sent through threads (can be disable to allow other solutions, like a Celery app)

.. toctree::
   :maxdepth: 2

   example
   tutorial
   templatetags
   settings
   templates


.. index::
   pair: Quick; Start

Quick start
===========

1. In your ``settings.py``:

 * Add ``django.contrib.comments`` and ``django_comments_xtd`` to ``INSTALLED_APPS``
 * Add ``COMMENTS_APP = "django_comments_xtd"``
 * Add ``COMMENTS_XTD_MAX_THREAD_LEVEL = N``, being ``N`` the maximum level up to which comments can be threaded:

  * When N = 0: comments are not nested
  * When N = 1: comments can be bested at level 0
  * When N = K: comments can be nested up until level K-1

  This setting can also be set up on a per ``<app>.<model>`` basis so that you can enable different thread levels for different models. ie: no nested comment for blog posts, up to one thread level for book reviews...

  Read more about ``COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL`` in the :doc:`tutorial` and see it in action in the **multiple** demo site in :doc:`example`.

 * Customize your project's email settings:

  * ``EMAIL_HOST = "smtp.mail.com"``
  * ``EMAIL_PORT = "587"``
  * ``EMAIL_HOST_USER = "alias@mail.com"``
  * ``EMAIL_HOST_PASSWORD = "yourpassword"``
  * ``DEFAULT_FROM_EMAIL = "Helpdesk <helpdesk@yourdomain>"``

2. If you want to allow comments written in markup languages like Markdown or reStructuredText:

 * Get the dependencies: `django-markup <https://github.com/bartTC/django-markup>`_
 * And add ``django_markup`` to ``INSTALLED_APPS``

3. Add ``url(r'^comments/', include('django_comments_xtd.urls'))`` to your root URLconf.

4. Change templates to introduce comments:

 * Load the ``comments`` templatetag and use their tags (ie: in your ``templates/app/model_detail.html`` template):

  * ``{% get_comment_count for object as comment_count %}``
  * ``{% render_comment_list for object %}`` (uses ``comments/list.html``)
  * ``{% render_comment_form for post %}`` (uses ``comments/form.html`` and ``comments/preview.html``)

 * Load the ``comments_xtd`` templatetag and use their tags and filter:

  * ``{% get_xtdcomment_count as comments_count for blog.story blog.quote %}``
  * ``{% render_last_xtdcomments 5 for blog.story blog.quote using "blog/comment.html" %}``
  * ``{% get_last_xtdcomments 5 as last_comments for blog.story blog.quote %}``
  * Filter render_markup_comment: ``{{ comment.comment|render_markup_comment }}``. You may want to copy and change the template ``comments/list.html`` from ``django.contrib.comments`` to use this filter.

5. ``syncdb``, ``runserver``, and

6. Hit your App's URL!

7. Have questions? Keep reading, and look at the 3 demo sites.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
