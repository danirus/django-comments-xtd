.. _ref-quickstart:

.. index::
   single: Guide
   pair: Quick; Start

=================
Quick start guide
=================

To get started using django-comments-xtd follow these steps:

#. ``pip install django-comments-xtd``

#. :ref:`Enable the "sites" framework <enabling-the-sites-framework>` by adding ``'django.contrib.sites'`` to :setting:`INSTALLED_APPS` and defining :setting:`SITE_ID`. Visit the admin site and be sure that the domain field of the ``Site`` instance points to the correct domain (``localhost:8000`` when running the default development server), as it will be used to create comment verification URLs, follow-up cancellations, etc.

#. Add ``'django_comments_xtd'`` and ``'django_comments'``, in that order, to :setting:`INSTALLED_APPS`.

#. Set the :setting:`COMMENTS_APP` setting to ``'django_comments_xtd'``.

#. Set the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL` to ``N``, being ``N`` the maximum level of threading up to which comments will be nested in your project.

   .. code-block:: python

       # 0: No nested comments:
       #  Comment (level 0)
       # 1: Nested up to level one:
       #  Comment (level 0)
       #   |-- Comment (level 1)
       # 2: Nested up to level two:
       #  Comment (level 0)
       #   |-- Comment (level 1)
       #        |-- Comment (level 2)
       COMMENTS_XTD_MAX_THREAD_LEVEL = 2

   The thread level can also be established on a per ``<app>.<model>`` basis by using the :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL` setting. Use it to establish different maximum threading levels for each model. ie: no nested comments for quotes, up to thread level 2 for blog stories, etc.

#. Set the :setting:`COMMENTS_XTD_CONFIRM_EMAIL` to ``True`` to require comment confirmation by email for no logged-in users.

#. Run ``manage.py migrate`` to create the tables.

#. Add the URLs of the comments-xtd app to your project's ``urls.py``:

   .. code-block:: python

       urlpatterns = [
           ...
           url(r'^comments/', include('django_comments_xtd.urls')),
           ...
       ]

#. Customize your project's email settings:

   .. code-block:: python

       EMAIL_HOST = "smtp.mail.com"
       EMAIL_PORT = "587"
       EMAIL_HOST_USER = "alias@mail.com"
       EMAIL_HOST_PASSWORD = "yourpassword"
       DEFAULT_FROM_EMAIL = "Helpdesk <helpdesk@yourdomain>"

#. To allow a quick start django-comments-xtd makes use of `twitter-bootstrap`_. From django-comments-xtd v2.3 on it uses Twitter-Bootstrap v4. From django-comments-xtd v1.7.1 to v2.2 it uses Twitter-Bootstrap v3. If you want to build your own templates, use the `comments <https://django-contrib-comments.readthedocs.io/en/latest/quickstart.html#comment-template-tags>`_ templatetag module, provided by the `django-comments <https://django-contrib-comments.readthedocs.io/en/latest/index.html>`_ app. Create a ``comments`` directory in your templates directory and copy the templates you want to customise from the Django Comments Framework. The following are the most important:

   * ``comments/list.html``, used by the ``render_comments_list`` templatetag.

   * ``comments/form.html``, used by the ``render_comment_form`` templatetag.

   * ``comments/preview.html``, used to preview the comment or when there are errors submitting it.

   * ``comments/posted.html``, which gets rendered after the comment is sent.

#. Add extra settings to control comments in your project. Check the available settings in the :ref:`Django Comments Framework <settings-comments>` and in the :ref:`django-comments-xtd app <settings-comments-xtd>`.


These are the steps to quickly start using django-comments-xtd. Follow to the next page, the :ref:`ref-tutorial`, to read a detailed guide that takes everything into account. In addition to the tutorial, the :ref:`ref-example` implement several commenting applications.


.. _twitter-bootstrap: https://getbootstrap.com
.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html

