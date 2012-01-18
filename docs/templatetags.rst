.. _ref-templatetags:

============
Templatetags
============

Django-comments-xtd comes with three tags:

 * ``get_xtdcomment_count``
 * ``get_last_xtdcomments``
 * ``render_last_xtdcomments``

To use any of them in your templates you first need to load them::

    {% load comments_xtd %}



``get_xtdcomment_count``
========================

Syntax::

    {% get_xtdcomment_count as [varname] for [app].[model] [[app].[model] ...] %}

Gets the comment count for the given pairs ``<app>.<model>`` and populates the template context with a variable containing that value, whose name is defined by the ``as`` clause.


Example usage
-------------

Get the count of comments the model ``Story`` of the app ``blog`` have received, and store it in the context variable ``comment_count``::

    {% get_xtdcomment_count as comment_count for blog.story %}

Get the count of comments two models, ``Story`` and ``Quote``, have received and store it in the context variable ``comment_count``::

    {% get_xtdcomment_count as comment_count for blog.story blog.quote %}


``get_last_xtdcomments``
========================

Syntax::

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


``render_last_xtdcomments``
===========================

Syntax::

    {% render_last_xtdcomments [N] for [app].[model] [[app].[model] ...] %}

Renders the list of the last N comments for the given pairs ``<app>.<model>`` using the following search list for templates:

 * ``django_comments_xtd/<app>/<model>/comment.html``
 * ``django_comments_xtd/<app>/comment.html``
 * ``django_comments_xtd/comment.html``

Example usage
-------------

Render the list of the last 5 comments posted, either to the blog.story model or to the blog.quote model. See it in action in the *Multiple Demo Site*, in the *blog homepage*, template ``blog/homepage.html``::

    {% render_last_xtdcomments 5 for blog.story blog.quote %}
