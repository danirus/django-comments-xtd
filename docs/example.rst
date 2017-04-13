.. _ref-example:

=============
Demo projects
=============

Django-comments-xtd comes with three demo projects:

1. **simple**: Single model with **non-threaded** comments
2. **custom**: Single model with comments provided by a new app that extends django-comments-xtd. The new comment model adds a ``title`` field to the XtdComment class. Find more details in :ref:`ref-extending`.
3. **comp**: Several models with maximum thread level defined on per app.model pair, moderation, removal suggestion flag, like/dislike flags, and list of users who liked/disliked comments.

Visit the **example** directory within the repository `in GitHub <http://github.com/danirus/django-comments-xtd/tree/master/example>`_ for a quick look.

.. contents:: Table of Contents
   :depth: 1
   :local:

.. index::
   pair: Demo; Setup 
   
Setup
=====

The recommended way to run the demo sites is in its own `virtualenv <http://www.virtualenv.org/en/latest/>`_. Once in a new virtualenv, clone the code and cd into any of the 3 demo sites. Then run the migrate command and load the data in the fixtures directory:

   .. code-block:: bash

    $ virtualenv venv
    $ source venv/bin/activate
    (venv)$ git clone git://github.com/danirus/django-comments-xtd.git
    (venv)$ cd django-comments-xtd/example/[simple|custom|comp]
    (venv)$ python manage.py migrate
    (venv)$ python manage.py loaddata ../fixtures/auth.json
    (venv)$ python manage.py loaddata ../fixtures/sites.json
    (venv)$ python manage.py loaddata ../fixtures/articles.json
    (venv)$ python manage.py runserver


Fixtures data provide:

 * An ``admin`` **User**, with password ``admin``
 * A default **Site** with domain ``localhost:8000`` so that URLs sent in mail messages use already the URL of the development web server of Django.
 * A couple of **Article** objects to which the user can post comments.

By default mails are sent directly to the console using the ``console.EmailBackend``. Comment out ``EMAIL_BACKEND`` in the settings module to send actual mails. You will need working values for all the ``EMAIL_`` settings.


.. index::
   single: Simple
   pair: Simple; Demo

Simple demo
===========

The simple example features:
  
 #. An Articles App, with a model ``Article`` whose instances accept comments.

 #. Confirmation by mail is required before the comment hit the database, unless ``COMMENTS_XTD_CONFIRM_EMAIL`` is set to False. Authenticated users don't have to confirm comments.
    
 #. Follow up notifications via mail.
    
 #. Mute links to allow cancellation of follow-up notifications.
    
 #. It uses the template tag ``render_markup_comment`` to render comment content. So you can use line breaks, Markdown or reStructuredText to format comments. To use special formatting, start the comment with the line ``#!<markup-lang>`` being ``<markup-lang>`` either ``markdown``, ``restructuredtext`` or ``linebreaks``.
      
 #. No nested comments.


Give it a try and test the features. Setup the project as explained above, run the development server, and visit http://localhost:8000/.

 * Log out from the admin site to post comments, otherwise they will be automatically confirmed and no email will be sent.
 * When adding new articles in the admin interface be sure to tick the box *allow comments*, otherwise comments won't be allowed.
 * Send new comments with the Follow-up box ticked and a different email address. You won't receive follow-up notifications for comments posted from the same email address the new comment is being confirmed from.
 * Click on the Mute link on the Follow-up notification email and send another comment. You will not receive further notifications.


.. index::
   single: custom
   pair: custom; demo

Custom demo
===========

The **simple_threads** demo site extends the **simple** demo functionality featuring:

 * Thread support up to level 2

1. Visit http://localhost:8000/ and look at the first article page with 9 comments.

2. See the comments in the admin interface too:

 * The first field represents the thread level.
 * When in a nested comment the first field refers to the parent comment.


.. index::
   single: Multiple
   pair: Multiple; Demo

Comp demo
=========

The **multiple** demo allows users post comments to three different type of instances: stories, quotes, and releases. Stories and quotes belong to the **blog app** while releases belong to the **projects app**. The demo shows the blog homepage with the last 5 comments posted to either stories or quotes and a link to the complete paginated list of comments posted to the blog. It features:

 * Definition of maximum thread level on a per app.model basis.
 * Use of comments_xtd template tags, ``get_xtdcomment_count``, ``render_last_xtdcomments``, ``get_last_xtdcomments``, and the filter ``render_markup_comment``.

1. Visit http://localhost:8000/ and take a look at the **Blog** and **Projects** pages. 

 * The **Blog** contains **Stories** and **Quotes**. Instances of both models have comments. The blog index page shows the **last 5 comments** posted to either stories or quotes. It also gives access to the **complete paginated list of comments**. 

 * Project releases have comments as well but are not included in the complete paginated list of comments shown in the blog. 

2. To render the last 5 comments the site uses:

 * The templatetag ``{% render_last_xtdcomments 5 for blog.story blog.quote %}``

 * And the following template files from the ``demos/multiple/templates`` directory: 

  * ``django_comments_xtd/blog/story/comment.html`` to render comments posted to **stories**

  * ``django_comments_xtd/blog/quote/comment.html`` to render comments posted to **quotes**

 * You may rather use a common template to render comments:

  * For all blog app models: ``django_comments_xtd/blog/comment.html``

  * For all the website models: ``django_comments_xtd/comment.html``

3. To render the complete paginated list of comments the site uses:

 * An instance of a generic ``ListView`` class declared in ``blog/urls.py`` that uses the following queryset:

  * ``XtdComment.objects.for_app_models("blog.story", "blog.quote")``

4. The comment posted to the story **Net Neutrality in Jeopardy** starts with a specific line to get the content rendered as reStructuredText. Go to the admin site and see the source of the comment; it's the one sent by Alice to the story 2.

 * To format and render a comment in a markup language, make sure the first line of the comment looks like: ``#!<markup-language>`` being ``<markup-language>`` any of the following options:

  * markdown
  * restructuredtext
  * linebreaks

 * Then use the filter ``render_markup_comment`` with the comment field in your template to interpret the content (see ``demos/multiple/templates/comments/list.html``).
