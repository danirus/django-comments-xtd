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
to prevent non-registered users from seeing the post comment form and rather
display a message inviting them to login or register.

As an example, here below there is a modified version of the
``article_detail.html`` template of the simple example project, that displays
a message with a link to the login page when the user is not authenticated:

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
          <p class="text-center">
            Only registered users can post comments. Please,
            <a href="{% url 'admin:login' %}?next={{ object.get_absolute_url }}">login</a>.
          </p>
        {% endif %}
      {% else %}
      <h5 class="text-center">comments are disabled for this article</h5>
      {% endif %}

    [...]


Using Django and JavaScript
===========================

This section goes through the steps to customize the :ref:`example-comp` to
prevent that unregistered users post comments.

The :ref:`example-comp` contains two apps, articles and quotes, that can
receive comments. The articles app uses the JavaScript plugin and the REST
API, while the quotes app uses merely the backend. Both apps allow registered
users and visitors to post nested comments. While only registered users can
send like/dislike flags.

Let is customize the project.


Customize the quotes app of the comp project
--------------------------------------------

If you have already setup the :ref:`example-comp`, and have sent a few
testing comments to see that visitors and registered users can comment, edit
the :setting:`COMMENTS_XTD_APP_MODEL_OPTIONS` at the bottom of the
``settings.py`` and append the pair ``'who_can_post': 'users'`` to the
quotes app:

   .. code-block:: python

       COMMENTS_XTD_APP_MODEL_OPTIONS = {
           'quotes.quote': {
               'allow_flagging': True,
               'allow_feedback': True,
               'show_feedback': True,
               'who_can_post': 'users'
           }
       }

Now restart the runserver command and see that registered users can comment
without issues. However visitors get the HTTP-400 page (Bad Request).

One last customization has to be done to prevent the HTTP-400 Bad Request. We
have to edit the ``templates/quotes/quote_detail.html`` file and be sure
that the if-block that contains the ``{% render_comment_form %}`` tag looks
like the following:

   .. code-block:: html+django

    [...] around line 41...

        {% if object.allow_comments %}
          {% if object|can_receive_comments_from:user %}
            <div class="card card-block mt-4 mb-5">
              <div class="card-body">
                <h4 class="card-title text-center pb-3">Post your comment</h4>
                {% render_comment_form for object %}
              </div>
            </div>
          {% else %}
            <p class="mt-4 mb-5 text-center">
              Only registered users can post comments. Please,
              <a href="{% url 'admin:login' %}?next={{ object.get_absolute_url }}">login</a>.
            </p>
          {% endif %}
        {% else %}
          <h4 class="mt-4 mb-5 text-center text-secondary">
            Comments are disabled for this quote.
          </h4>
        {% endif %}

    [...]

In the previous snippet we use the template filter
:ttag:`can_receive_comments_from`. Using this filter you could change the
setting ``'who_can_post'`` to ``'all'`` in your
:setting:`COMMENTS_XTD_APP_MODEL_OPTIONS` to allow mere visitors to also post
comments, and your template would display the comment form without any further
change.

If you rather had used ``{% if user.is_authenticated %}`` your template would
not allow visitors to see the comment form. Even with a
``'who_can_post': 'all'``

See that after the changes, you can only post comments as a registered user.
See also that the **Reply** link to send nested comments is already aware of
the value of the ``'who_can_post'`` setting and behaves accordingly.


Setup your Django project so that django-comments-xtd will allow only signed in users to post comments.

 * commentbox.jsx control whether the user in the session can post comments or not. If she cannot, we inform the user of such a condition. There are two ways to inform the user:
    1. We display a hardcoded message provided within the JavaScript Plugin. Specifically in the function render_comment_form of the commentbox.jsx module.
    1. We load an HTML element with a given ID and display it using the dangerouslySetInnerHTML. The HTML element is loaded in the article_detail.html via a templatetag. The templatetag will add the HTML element with an ID that changes when the page is reloaded. The ID is generated using a function that is also used by the frontend.py's commentsbox_props function. Doing so when the page reloads, both, the HTML Element with the customized message loaded via the templatetag, and the props passed to the JavaScript plugin, will use the same ID. Thus the JavaScript plugin will know what ID to load. In order to produce the same ID I have to use middleware, so that I store it in the session and I fetch it from there.
