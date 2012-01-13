.. _ref-example:

============
Demo project
============

Django-comments-xtd comes with a demo project to see the app in action.

The demo project provides the minimum extra development to use the django-comments-xtd app. This minimum consist of an app called **articles** whose model **Article**' instances may accept comments. 

This demo project is an example of how to add comments to those articles by using the built-in `Django Comments Framework <https://docs.djangoproject.com/en/1.3/ref/contrib/comments/>`_ and **Django-comments-xtd**.

Demo setup
==========

1. Go to the ``django_comments_xtd/demo`` directory.

2. Customise *email settings* at the end of the ``settings.py`` file.

3. Do ``python manage syncdb --noinput`` to create a simple SQLite db file for the demo. Admin access granted for ``admin``, password ``admin``.

4. Run the server: ``python manage runserver``

Demo in action
==============

1. Visit http://localhost:8000/ and look at your articles' detail page. 

2. As ``COMMENTS_XTD_LIST_URL`` is ``True`` in the demo site the comments list page is active:
 * Visit http://localhost:8000/comments/list/
 * Change the ``COMMENTS_XTD_LIST_PAGINATE_BY`` to paginate by any count of comments.

3. Try to post comments:
 * Logged out, to receive confirmation requests by email
 * Logged in, to get your comments accepted without requiring confirmation

4. When adding new articles in the admin interface be sure to tick the box *allow comments*, otherwise comments won't be allowed.
