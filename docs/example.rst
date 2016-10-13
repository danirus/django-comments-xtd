.. _ref-example:

=============
Demo projects
=============

Django-comments-xtd comes with three demo projects:

1. **simple**: Single model with **non-threaded** comments
2. **simple_threads**: Single model with **threaded** comments up to level 2
3. **multiple**: Several models with comments, and a maximum thread level defined for each app.model pair.
4. **custom_comments**: Single model with comments provided by a new app that extends django-comments-xtd. Comments have a new ``title`` field. Find more details in :ref:`ref-extending`.

`Click here <http://github.com/danirus/django-comments-xtd/tree/master/django_comments_xtd/demos>`_ for a quick look at the examples directory in the repository.


.. index::
   pair: Demo; Setup 

Demo sites setup
================

The recommended way to run the demo sites is in its own `virtualenv <http://www.virtualenv.org/en/latest/>`_. Once in a new virtualenv, clone the code and cd into any of the 3 demo sites. Then run the install script and launch the dev server::

    $ git clone git://github.com/danirus/django-comments-xtd.git
    $ cd django-comments-xtd/django_comments_xtd/demos/[simple|simple_thread|multiple]
    $ pip install ../../requirements.pip
    $ sh ./install.sh (to syncdb, migrate and loaddata)
    $ python manage.py runserver

By default:
 * There's an ``admin`` user, with password ``admin``
 * Emails are sent to the ``console.EmailBackend``. Comment out ``EMAIL_BACKEND`` in the settings module to send actual emails.


.. index::
   single: Simple
   pair: Simple; Demo

Simple demo site
================

The **simple** demo site is a project with just one application called **articles** with an **Article** model whose instances accept comments. The example features: 

 * Comments have to be confirmed by email before they hit the database. 
 * Users may request follow-up notifications.
 * Users may cancel follow-up notifications by clicking on the mute link.

Follow the next steps to give them a try:
 
1. Visit http://localhost:8000/ and look at your articles' detail page. 

2. Log out of the admin site to post comments, otherwise they will be automatically confirmed and no email will be sent.

3. When adding new articles in the admin interface be sure to tick the box *allow comments*, otherwise comments won't be allowed.

4. Send new comments with the Follow-up box ticked and a different email address. You won't receive follow-up notifications for comments posted from the same email address the new comment is being confirmed from.

5. Click on the Mute link on the Follow-up notification email and send another comment. 

.. index::
   single: Simple_threads
   pair: Simple_treads; Demo

Simple with threads
===================

The **simple_threads** demo site extends the **simple** demo functionality featuring:

 * Thread support up to level 2

1. Visit http://localhost:8000/ and look at the first article page with 9 comments.

2. See the comments in the admin interface too:

 * The first field represents the thread level.
 * When in a nested comment the first field refers to the parent comment.


.. index::
   single: Multiple
   pair: Multiple; Demo

Multiple demo site
==================

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
