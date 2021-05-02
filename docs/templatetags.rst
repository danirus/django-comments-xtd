.. _ref-templatetags:

.. index::
   pair: Filters; Templatetags

=========================
Filters and template tags
=========================

Django-comments-xtd provides 5 template tags and 3 filters. Load the module to make use of them in your templates::

    {% load comments_xtd %}

.. contents:: Table of Contents
   :depth: 1
   :local:


.. index::
   single: can_receive_comments_from
   pair: filter; can_receive_comments_from

.. templatetag:: can_receive_comments_from

Filter ``can_receive_comments_from``
====================================

Filter syntax::

  {{ object|can_receive_comments_from:user }}

Returns True depending on the value of the ``'who_can_post'`` entry in the
:setting:`COMMENTS_XTD_APP_MODEL_OPTIONS`.
