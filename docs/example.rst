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
3. Do ``python manage syncdb`` to create a simple SQLite db file for the demo.
4. Run the server ``python manage runserver``
5. Visit http://localhost:8000/admin/ and:
  * Go to *Sites* and replace ``example.com`` with ``localhost:8000``
  * Go to *Articles* and add a couple of items, be sure to tick the box *allow comments*, otherwise comments won't be allowed.
6. Visit http://localhost:8000/ and visit your articles' detail page.
7. Try to post comments:
  * Logged out, to receive confirmation requests by email
  * Logged in, to get your comments accepted without requiring confirmation
