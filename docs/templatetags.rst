.. _ref-templatetags:

.. index::
   pair: Filters; Templatetags

=========================
Filters and Template Tags
=========================

Django-comments-xtd comes with three tags and one filter:

 * Tag ``get_xtdcomment_count``
 * Tag ``get_last_xtdcomments``
 * Tag ``render_last_xtdcomments``
 * Filter ``render_markup_comment``

To use any of them in your templates you first need to load them::

    {% load comments_xtd %}


.. index::
   single: get_xtdcomment_count
   pair: tag; get_xtdcomment_count

Get Xtdcomment Count
====================

Tag syntax::

    {% get_xtdcomment_count as [varname] for [app].[model] [[app].[model] ...] %}

Gets the comment count for the given pairs ``<app>.<model>`` and populates the template context with a variable containing that value, whose name is defined by the ``as`` clause.


Example usage
-------------

Get the count of comments the model ``Story`` of the app ``blog`` have received, and store it in the context variable ``comment_count``::

    {% get_xtdcomment_count as comment_count for blog.story %}

Get the count of comments two models, ``Story`` and ``Quote``, have received and store it in the context variable ``comment_count``::

    {% get_xtdcomment_count as comment_count for blog.story blog.quote %}


.. index::
   single: get_last_xtdcomments
   pair: tag; get_last_xtdcomments

Get Last Xtdcomments
====================

Tag syntax::

    {% get_last_xtdcomments [N] as [varname] for [app].[model] [[app].[model] ...] %}

Gets the list of the last N comments for the given pairs ``<app>.<model>`` and stores it in the template context whose name is defined by the ``as`` clause.

Example usage
-------------

Get the list of the last 10 comments two models, ``Story`` and ``Quote``, have received and store them in the context variable ``last_10_comment``. You can then loop over the list with a ``for`` tag::

    {% get_last_xtdcomments 10 as last_10_comments for blog.story blog.quote %}
    {% if last_10_comments %}
      {% for comment in last_10_comments %}
        <p>{{ comment.comment|linebreaks }}</p> ...
      {% endfor %}
    {% else %}
      <p>No comments</p>
    {% endif %}


.. index::
   single: render_last_xtdcomments
   pair: tag; render_last_xtdcomments

Render Last Xtdcomments
=======================

Tag syntax::

    {% render_last_xtdcomments [N] for [app].[model] [[app].[model] ...] %}

Renders the list of the last N comments for the given pairs ``<app>.<model>`` using the following search list for templates:

 * ``django_comments_xtd/<app>/<model>/comment.html``
 * ``django_comments_xtd/<app>/comment.html``
 * ``django_comments_xtd/comment.html``

Example usage
-------------

Render the list of the last 5 comments posted, either to the blog.story model or to the blog.quote model. See it in action in the *Multiple Demo Site*, in the *blog homepage*, template ``blog/homepage.html``::

    {% render_last_xtdcomments 5 for blog.story blog.quote %}


.. index::
   single: render_markup_comment, Markdown; reStructuredText
   pair: filter; render_markup_comment

Render Markup Comment
=====================

Filter syntax::

    {{ comment.comment|render_markup_comment }}


Renders a comment using a markup language specified in the first line of the comment.

Example usage
-------------

A comment like::

    comment = r'''#!markdown\n\rAn [example](http://url.com/ "Title")'''

Would be rendered as a markdown text, producing the output::

    <p><a href="http://url.com/" title="Title">example</a></p>

Markup languages available are:

 * `Markdown <http://daringfireball.net/projects/markdown/syntax>`_ (use ``#!markdown``)
 * `reStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_ (use ``#!restructuredtext``)
 * Linebreaks (use ``#!linebreaks``)
