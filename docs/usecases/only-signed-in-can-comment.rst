.. _ref-recipe-only-signed-in-can-comment:

================================
Only signed in users can comment
================================

This page describes how to setup django-comments-xtd so that only registered
users can write comments or flag them.


.. contents:: Table of Contents
   :depth: 1
   :local:

Using only Django
=================

A simple site using django-comments-xtd can be represented by the
:ref:`example-simple`.


Customize the simple project
----------------------------

The :ref:`example-simple` is a basic example site that allows both, visitors and
registered users, post comments to articles. The example loads a couple of
articles to illustrate the functionality.

If you have already setup the :ref:`example-simple`, and have sent a few
testing comments to see that visitors and registered users can comment, add the
:setting:`COMMENTS_XTD_APP_MODEL_OPTIONS` entry at the bottom of
the ``settings.py`` module:

   .. code-block:: python

       COMMENTS_XTD_APP_MODEL_OPTIONS = {
           'default': {
               'allow_flagging': False,
               'allow_feedback': False,
               'show_feedback': False,
               'who_can_post': 'users'
           }
       }

Now restart the runserver command and see that registered users can comment
without issues. However visitors get the HTTP-400 page (Bad Request).

As a final step to customize the simple example site either edit the
``templates/comments/form.html`` template or the
``templates/articles/article_detail.html`` template,
to prevent non-registered users from posting comments.

Following is a modified version of the ``article_detail.html`` template of the
simple example project, that displays a message with a link to the login page
when the user is not authenticated:

   .. code-block:: html+django

    [...]

      {% if object.allow_comments %}
        {% if user.is_authenticated %}
          <div class="comment">
            <h5 class="text-center">Post your comment</h5>
            <div class="well my-4">
              {% render_comment_form for object %}
            </div>
          </div>
        {% else %}
          <p  class="text-center">
            Only registered users can post comments. Please,
            <a href="{% url 'login' %}">login</a>.
          </p>
        {% endif %}
      {% else %}
      <h5 class="text-center">comments are disabled for this article</h5>
      {% endif %}

    [...]



Customize the quotes app of the comp project
--------------------------------------------


Using Django and JavaScript
===========================



Setup your Django project so that django-comments-xtd will allow only signed in users to post comments.

 * commentbox.jsx control whether the user in the session can post comments or not. If she cannot, we inform the user of such a condition. There are two ways to inform the user:
    1. We display a hardcoded message provided within the JavaScript Plugin. Specifically in the function render_comment_form of the commentbox.jsx module.
    1. We load an HTML element with a given ID and display it using the dangerouslySetInnerHTML. The HTML element is loaded in the article_detail.html via a templatetag. The templatetag will add the HTML element with an ID that changes when the page is reloaded. The ID is generated using a function that is also used by the frontend.py's commentsbox_props function. Doing so when the page reloads, both, the HTML Element with the customized message loaded via the templatetag, and the props passed to the JavaScript plugin, will use the same ID. Thus the JavaScript plugin will know what ID to load. In order to produce the same ID I have to use middleware, so that I store it in the session and I fetch it from there.
