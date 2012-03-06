.. _ref-example:

=============
Demo projects
=============

Django-comments-xtd comes with two demo projects to see the app in action:

 1. The Simple Model Demo Site
 2. The Multiple Model Demo Site

The *Simple Demo Site* provides the minimum stuff to use *django-comments-xtd*. It consists of an app called **articles** with an **Article** model. Instances of **Article** accept comments.

The *Multiple Demo Site* is a website that allows the user to post comments to three different type of instances: stories, quotes, and project releases. Stories and quotes belong to the **blog app** and project releases belong to the **projects app**. The demo shows the blog homepage with the last 5 comments posted to either stories or quotes and a link to the complete paginated list of comments.

These two demo projects are examples of how to use the built-in `Django Comments Framework <https://docs.djangoproject.com/en/1.3/ref/contrib/comments/>`_ with *Django-comments-xtd*.

Demo sites setup
================

1. Go to the demos directory ``django_comments_xtd/demos`` and choose either the  ``simple/`` or the ``multiple/`` models demo project.

2. Customise *email settings* at the end of the ``settings.py`` file.

3. Do ``python manage syncdb --noinput`` to create a simple SQLite db file for the demo (``user:admin``, ``pwd:admin``).


Simple demo site
================

1. Run ``python manage runserver`` in the ``simple`` directory.
2. Visit http://localhost:8000/ and look at your articles' detail page. 

3. Try to post comments:

 * Logged out, to receive confirmation requests by email

 * Logged in, to get your comments accepted without requiring confirmation

4. When adding new articles in the admin interface be sure to tick the box *allow comments*, otherwise comments won't be allowed.


Multiple demo site
==================

1. Run ``python manage runserver`` in the ``multiple`` directory.
2. Visit http://localhost:8000/ and take a look at the **Blog** and **Projects** pages. 

 * The **Blog** contains **Stories** and **Quotes**. Instances of both models have comments. The blog index page shows the **last 5 comments** posted to either stories or quotes. It also gives access to the **complete paginated list of comments**. 

 * Project releases have comments as well but are not included in the complete paginated list of comments shown in the blog. 

3. To render the last 5 comments the site uses:

 * The templatetag ``{% render_last_xtdcomments 5 for blog.story blog.quote %}``

 * And the following template files from the ``demos/multiple/templates`` directory: 

  * ``django_comments_xtd/blog/story/comment.html`` to render comments posted to **stories**

  * ``django_comments_xtd/blog/quote/comment.html`` to render comments posted to **quotes**

 * You may rather use a common template to render comments:

  * For all blog app models: ``django_comments_xtd/blog/comment.html``

  * For all the website models: ``django_comments_xtd/comment.html``

4. To render the complete paginated list of comments the site uses:

 * An instance of a generic ``ListView`` class declared in ``blog/urls.py`` that uses the following queryset:

  * ``XtdComment.objects.for_app_models("blog.story", "blog.quote")``

5. Comments posted to the story **Net Neutrality in Jeopardy** starts with a specific line to have the comment interpreted as reStructuredText. Go to the admin site and see the source of the comment; is the one sent by Alice to the story 2.

 * To format and render a comment in a markup language, make sure the first line of the comment looks like: ``#!<markup-language>`` being ``<markup-language>`` any of the following options:

  * markdown
  * restructuredtext
  * linebreaks

 * Then use the filter ``render_markup_comment`` with the comment field in your template to interpret the content (see ``demos/multiple/templates/comments/list.html``).
