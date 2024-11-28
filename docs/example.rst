.. _ref-example:

=============
Demo projects
=============

There are three example projects available within `django-comments-xtd's GitHub
repository <https://github.com/danirus/django-comments-xtd
/tree/master/example>`_.

The **simple project** provides non-threaded comment support to articles.
It's an only-backend project, meant as a test case of the basic features
(confirmation by mail, follow-up notifications, mute link).

The **custom project** provides threaded comment support to articles using a
new comment class that inherits from django-comments-xtd's. The new comment
model adds a ``title`` field to the ``XtdComment`` class. Find more details
in :ref:`ref-extending`.

The **comp project** provides comments to an ``Article`` model and a ``Quote``
model. Comments for Quotes show how to use django-comments-xtd as a pure Django
backend application. On the other hand, comments for Articles illustrate how
to use the app in combination with the JavaScript plugin. The project allows
nested comments and defines the maximum thread level on per ``app.model`` basis.
It uses moderation, removal suggestion flag, like/dislike flags, and displays the list of users who like or dislike comments.

Visit the **example** directory within the repository `in GitHub
<http://github.com/danirus/django-comments-xtd/tree/master/example>`_ for a
quick look.

.. contents:: Table of Contents
   :depth: 1
   :local:

.. index::
   pair: Demo; Setup

.. _example-setup:

Setup
=====

This section goes through the steps to setup any of the example projects.

Clone the source code, create the virtual environment and install the Python package and its dependencies:

.. code-block:: bash

    git clone git://github.com/danirus/django-comments-xtd.git
    cd django-comments-xtd/
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .

.. admonition:: optional

   The JavaScript plugin is already part of the repository. It is available in the ``static/django_comments_xtd/js`` directory. So it does not have to be built. You can skip the following step about preparing the NodeJS environment.

Prepare the NodeJS environment required to build the plugin. I recommend using `nvm <https://github.com/nvm-sh/nvm>`_ to set it up. Once you have ``nvm`` installed, use the stable version:

.. code-block:: bash

   nvm use stable
   npm install
   npm run compile
   npm run minify


Then, cd into the example project your prefer, load the data and run the development server:

.. code-block:: bash

    cd ../example/[simple|custom|comp]
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py loaddata ../fixtures/auth.json
    python manage.py loaddata ../fixtures/sites.json
    python manage.py loaddata ../fixtures/articles.json
    # The **comp** example project needs quotes.json too:
    python manage.py loaddata ../fixtures/quotes.json
    python manage.py runserver

Data fixtures provide:

- A User ``admin``, with password ``admin``.
- A default Site with domain ``localhost:8000`` to make comment confirmations work locally.
- A couple of article objects to which the user can post comments.

By default mails are sent directly to the console using the ``console.EmailBackend``. Comment out ``EMAIL_BACKEND`` in the settings module to send
actual mails. You will need to provide working values for all ``EMAIL_*``
settings.


.. index::
   single: Simple
   pair: Simple; Demo

.. _example-simple:

Simple project
==============

The simple example project features:

#. An Articles App, with a model ``Article`` whose instances accept comments.
#. Confirmation by mail is required before the comment hit the database, unless ``COMMENTS_XTD_CONFIRM_EMAIL`` is set to False. Authenticated users don't have to confirm comments.
#. Follow up notifications via mail.
#. Mute links to allow cancellation of follow-up notifications.
#. No nested comments.


This example project tests the initial features provided by
django-comments-xtd. Setup the project as explained above.

Some hints:
 * Log out from the admin site to post comments, otherwise they will be
   automatically confirmed and no email will be sent.
 * When adding new articles in the admin interface be sure to tick the box
   *allow comments*, otherwise comments won't be allowed.
 * Send new comments with the Follow-up box ticked and a different email
   address. You won't receive follow-up notifications for comments posted from
   the same email address the new comment is being confirmed from.
 * Click on the Mute link on the Follow-up notification email and send another
   comment. You will not receive further notifications.


.. index::
   single: custom
   pair: custom; demo

Custom project
==============

The **custom** example project extends the **simple** project functionality
featuring:

- Thread support up to level 2
- A new comment class that inherits from ``XtdComment`` with a new ``title`` field and a new form class.

.. cs_image:: images/extend-comments-app.png
   :width: 95%
   :align: center
   :class: border-radius-1


.. index::
   single: Multiple
   pair: Multiple; Demo

.. _example-comp:

Comp project
============

The Comp Demo implements two apps, each of which contains a model whose
instances can received comments:

* App ``articles`` with the model ``Article``
* App ``quotes`` with the model ``Quote``

Features:

#. Comments can be nested, and the maximum thread level is established to 2.
#. Comment confirmation via mail when the users are not authenticated.
#. Comments hit the database only after they have been confirmed.
#. Follow up notifications via mail.
#. Mute links to allow cancellation of follow-up notifications.
#. Registered users can like/dislike comments and can suggest comments removal.
#. Registered users can see the list of users that liked/disliked comments.
#. The homepage presents the last 5 comments posted either to the ``articles.Article`` or the ``quotes.Quote`` model.


Threaded comments
-----------------

The setting ``COMMENTS_XTD_MAX_THREAD_LEVEL`` is set to 2, meaning that comments
may be threaded up to 2 levels below the the first level (internally known as
level 0)::

    First comment (level 0)
        |-- Comment to "First comment" (level 1)
            |-- Comment to "Comment to First comment" (level 2)

``render_xtdcomment_tree``
--------------------------

By using the ``render_xtdcomment_tree`` templatetag, ``quote_detail.html``, show
the tree of comments posted. Addind the argument ``allow_feedback`` users can
send like/dislike feedback. Adding the argument ``show_feedback`` allow visitors
see other users like/dislike feedback. And adding ``allow_flagging`` allow users
flag comments for removal.

``render_last_xtdcomments``
---------------------------

The **Last 5 Comments** shown in the block at the rigght uses the templatetag
``render_last_xtdcomments`` to show the last 5 comments posted to either
``articles.Article`` or ``quotes.Quote`` instances. The templatetag receives the
list of pairs ``app.model`` from which we want to gather comments and shows the
given N last instances posted. The templatetag renders the template
``django_comments_xtd/comment.html`` for each comment retrieve.

JavaScript plugin
-----------------

As opposed to the ``Quote`` model, the ``Article`` model receives comments via the provided JavaScript plugin. Check the :doc:`javascript` page to know more.
