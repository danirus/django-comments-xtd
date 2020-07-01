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

As a final step to customize the simple example site either edit
``templates/comments/form.html`` or ``templates/articles/article_detail.html``
to display a message inviting visitors to login or register instead of showing
the post comment form.

As an example, here is a modified version of ``article_detail.html`` that
displays a message with a link to the login page when the user is not
authenticated:

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

This section goes through the steps to customize a project that uses the
backend side of djando-comments-xtd, with the REST API, and the JavaScript
opinionated plugin to prevent that unregistered users post comments.

For such goal we use will the :ref:`example-comp`.

The :ref:`example-comp` contains two apps, articles and quotes, that can
receive comments. The articles app uses the JavaScript plugin and the REST
API, while the quotes app uses merely the backend. Both apps allow registered
users and visitors to post nested comments. While only registered users can
send like/dislike flags.


Customize the quotes app of the comp project
--------------------------------------------

If you have already setup the :ref:`example-comp`, and have sent a few
testing comments to see that visitors and registered users can comment, edit
the :setting:`COMMENTS_XTD_APP_MODEL_OPTIONS` at the bottom of the
``settings.py`` and append the pair ``'who_can_post': 'users'`` to the
quotes app dictionary:

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
without issues. However visitors however get the HTTP-400 page (Bad Request).

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

.. note::

    In the previous snippet we use the template filter
    :ttag:`can_receive_comments_from`. Using this filter you could change the
    setting ``'who_can_post'`` to ``'all'`` in your
    :setting:`COMMENTS_XTD_APP_MODEL_OPTIONS` to allow mere visitors to post
    comments, and your template would do as expected without further changes.

    If we rather had used ``{% if user.is_authenticated %}`` the template would
    have still to be changed to display the comment form to all, visitors and
    registered users.

See that after the changes, you can only post comments as a registered user.
After you have sent a comment, see that the **Reply** link to send nested
comments is already aware of the value of the ``'who_can_post'`` setting and
redirects you to login if you have not logged in yet.


Customize the articles app of the comp project
----------------------------------------------

The articles app uses the JavaScript plugin that in turn uses the REST API.

The first change to do is to add the pair ``'who_can_post': 'users'`` to the
``'articles.article'`` dictionary entry of the
:setting:`COMMENTS_XTD_APP_MODEL_OPTIONS`, as we did with the quotes app. That
simple change will make it work.

Launch the runserver command and check that as a mere visitor (logout:
http://localhost:8000/admin/logout) you can not send comments to articles.
Instead there must be a boring message in blue saying that **Only registered
users can post comments.** If you login (http://localhost:8000/admin/login/)
and visit an article's page the post comment form becomes visible again.

The boring message is the default response of the ``commentbox.jsx``
module of the JavaScript plugin. The commentbox module controls whether the user
in the session can post comments or not. If the user can not post comments it
defaults to display that message in blue.

Most of the times we will want to customize the message. We will achieve it by
modifying both, the ``base.html`` and the ``articles/article_detail.html``, and
by creating a new template in the ``comp/templates/django_comments_xtd``
directory called ``only_users_can_post.html``.

The changes in ``templates/base.html`` consist of adding a hidden block. We will
put content in this hidden block in the ``articles_detail.html``. So far we just
add the following HTML code before the script tags:

   .. code-block:: html+django

    [...] around line 67, right before the first <script> tag...

        <div style="display:none">
          {% block hidden %}
          {% endblock %}
        </div>

    [...]

The changes in ``templates/articles/article_detail.html`` add content to
the hidden block:

   .. code-block:: html+django

    [...] around line 46, right before the {% block extra_js %}...

    {% block hidden %}
      {% render_only_users_can_post_template object %}
    {% endblock %}

And finally we create the file ``only_users_can_post.html`` within the
``comp/templates/django_comments_xtd`` directory, and add the following content
to it:

   .. code-block:: html+django

    <div id="only-users-can-post-{{ html_id_suffix }}">
      <p>Only registered users can post comments. Please,
        <a href="{% url 'admin:login' %}?next={{ object.get_absolute_url }}">login</a>.
      </p>
    </div>

Now logout of the comp site (http://localhost:8000/admin/logout/) and reload the
article's page. You should see

In this hidden block we will place the HTML content that will be displayed to
visitors instead of the post comment form.

In the quotes app we did that by modifiying the ``quote_detail.html`` template.
But for the articles app we use the JavaScript plugin.

Setup your Django project so that django-comments-xtd will allow only signed in users to post comments.

 * commentbox.jsx control whether the user in the session can post comments or not. If she cannot, we inform the user of such a condition. There are two ways to inform the user:
    1. We display a hardcoded message provided within the JavaScript Plugin. Specifically in the function render_comment_form of the commentbox.jsx module.
    1. We load an HTML element with a given ID and display it using the dangerouslySetInnerHTML. The HTML element is loaded in the article_detail.html via a templatetag. The templatetag will add the HTML element with an ID that changes when the page is reloaded. The ID is generated using a function that is also used by the frontend.py's commentsbox_props function. Doing so when the page reloads, both, the HTML Element with the customized message loaded via the templatetag, and the props passed to the JavaScript plugin, will use the same ID. Thus the JavaScript plugin will know what ID to load. In order to produce the same ID I have to use middleware, so that I store it in the session and I fetch it from there.
