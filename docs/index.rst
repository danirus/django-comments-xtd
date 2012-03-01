.. django-comments-xtd documentation master file, created by
   sphinx-quickstart on Mon Dec 19 19:20:12 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

**django-comments-xtd** extends the built-in Django's Comments Framework with:

1. Optional notification of follow-up comments via email
2. Comment confirmation via email when users are not authenticated
3. Comments hit the database only when have been confirmed
4. Template tags to list/render the last N comments posted to any list of models
5. Several comments format: plain text, linebreaks, Markdown or reStructuredText


.. toctree::
   :maxdepth: 2

   example
   tutorial
   templatetags
   settings
   templates


Quick start
===========

1. Get the dependencies:

 * `django-markup <https://github.com/bartTC/django-markup>`_

1. In your ``settings.py``:

 * Add ``django.contrib.comments``, ``django_comments_xtd`` and ``django_markup`` to ``INSTALLED_APPS``.

 * Add ``COMMENTS_APP = "django_comments_xtd"``

 * Add ``COMMENTS_XTD_CONFIRM_EMAIL = True``

 * Customize your email settings (see :doc:`example`)

3. Add ``url(r'^comments/', include('django_comments_xtd.urls'))`` to your root URLconf.

4. Make changes in the templates of your models-with-comments. 

 * Load the ``comments`` templatetag and use their tags:

  * ``{% get_comment_count for object as comment_count %}``

  * ``{% render_comment_list for object %}`` (uses ``comments/list.html``)

  * ``{% render_comment_form for post %}`` (uses both ``comments/form.html`` and ``comments/preview.html``)

 * Load the ``comments_xtd`` templatetag and use their tags and filter:

  * ``{% get_xtdcomment_count as comments_count for blog.story blog.quote %}``

  * ``{% render_last_xtdcomments 5 for blog.story blog.quote using "blog/comment.html" %}``

  * ``{% get_last_xtdcomments 5 as last_comments for blog.story blog.quote %}``

  * Filter render_markup_comment: ``{{ comment.comment|render_markup_comment }}``

5. ``syncdb``, ``runserver``, and

6. Hit your App's URL!


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

