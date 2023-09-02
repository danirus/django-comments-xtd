.. _management-commands-comments-xtd:

===================
Management Commands
===================

There are two management commands you can use with django-comments-xtd.

.. contents:: Table of Contents
   :depth: 1
   :local:


.. _initialize_nested_count:

``initialize_nested_count``
===========================

Since v2.8.0 there is a new attribute in the ``XtdComment`` model: ``nested_count``. The attribute contains the number of comments nested under the comment instance.

If your project started using django-comments-xtd before v2.8.0 then you might want to feed ``nested_count`` with the correct values. The command ``initialize_nested_comment`` read your comments table and compute the correct value for ``nested_count`` for every comment.

The command is idempotent, so it is safe to run it more than once over the same database.

An example::

     $ python manage.py initialize_nested_count


.. _populate_xtd_comments:

``populate_xtd_comments``
=========================

Management command `populate_xtd_comments` helps to start using django-comments-xtd when your project is based on django-comments.

Read the section :ref:`ref-migrating` to know more about how to do the migration.
