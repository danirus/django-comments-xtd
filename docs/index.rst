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

.. toctree::
   :maxdepth: 2

   example
   tutorial
   templatetags
   settings
   templates


Quick start
===========

1. Add ``django.contrib.comments`` and ``django_comments_xtd`` to ``INSTALLED_APPS``.
2. In your ``settings.py``:
 * Add ``COMMENTS_APP = "django_comments_xtd"``
 * Add ``COMMENTS_XTD_CONFIRM_EMAIL = True``
 * Customize your email settings (see :doc:`example`)
3. Add ``url(r'^comments/', include('django_comments_xtd.urls'))`` to your root URLconf.
4. Customise the templates of the model you will add comments to: ``<your_app>/<your_model>_detail.html``, load the ``comments`` templatetag module and use its tags in your template:
  * ``{% get_comment_count for object as comment_count %}``
  * ``{% render_comment_list for object %}`` (uses ``comments/list.html``)
  * ``{% render_comment_form for post %}`` (uses both ``comments/form.html`` and ``comments/preview.html``)
5. ``syncdb``, ``runserver``, and
6. Hit your App's URL!


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

