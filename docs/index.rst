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
5. Comments formatted in Markdown, reStructuredText, linebreaks or plain text
6. Threaded emails to avoid response blocking

.. toctree::
   :maxdepth: 2

   example
   tutorial
   templatetags
   settings
   templates


Quick start
===========

1. In your ``settings.py``:

 * Add ``django.contrib.comments``, ``django_comments_xtd`` 
 * Add ``COMMENTS_APP = "django_comments_xtd"``
 * Add ``COMMENTS_XTD_CONFIRM_EMAIL = True``
 * Customize your email settings (see :doc:`example`)

2. If you want to allow comments written in markup languages like Markdown or reStructuredText:

 * Get the dependencies: `django-markup <https://github.com/bartTC/django-markup>`_
 * And add ``django_markup`` to ``INSTALLED_APPS``

3. Add ``url(r'^comments/', include('django_comments_xtd.urls'))`` to your root URLconf.

4. Change templates to introduce comments:

 * Load the ``comments`` templatetag and use their tags:

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

