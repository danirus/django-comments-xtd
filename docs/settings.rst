.. _settings-comments-xtd:

========
Settings
========

To use django-comments-xtd it is necessary to declare the
:setting:`COMMENTS_APP` setting in your project's settings module
as::

    COMMENTS_APP = "django_comments_xtd"

A number of additional settings are available to customize django-comments-xtd
behaviour.

.. contents:: Table of Contents
   :depth: 1
   :local:


.. setting:: COMMENTS_XTD_MAX_THREAD_LEVEL
   
``COMMENTS_XTD_MAX_THREAD_LEVEL``
=================================

**Optional**. Indicates the **Maximum thread level** for comments. In other
words, whether comments can be nested. This setting established the default
value for comments posted to instances of every model instance in Django. It
can be overriden on per app.model basis using the
:setting:`COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL`, introduced right after
this section.

An example::

     COMMENTS_XTD_MAX_THREAD_LEVEL = 8

It defaults to ``0``. What means nested comments are not permitted.


.. setting:: COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL

``COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL``
==============================================

**Optional**. The **Maximum thread level on per app.model basis** is a
dictionary with pairs `app_label.model` as keys and the maximum thread level
for comments posted to instances of those models as values. It allows
definition of max comment thread level on a per `app_label.model` basis.

An example::

    COMMENTS_XTD_MAX_THREAD_LEVEL = 0
    COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {
        'projects.release': 2,
	    'blog.stories': 8, 
        'blog.quotes': 8, 
	    'blog.diarydetail': 0 # Omit, defaults to COMMENTS_XTD_MAX_THREAD_LEVEL
    }

In the example, comments posted to ``projects.release`` instances can go up to
level 2::

    First comment (level 0)
        |-- Comment to "First comment" (level 1)
            |-- Comment to "Comment to First comment" (level 2)


It defaults to ``{}``. What means the maximum thread level is setup
with :setting:`COMMENTS_XTD_MAX_THREAD_LEVEL`.
    

.. setting:: COMMENTS_XTD_CONFIRM_EMAIL

``COMMENTS_XTD_CONFIRM_EMAIL``
==============================

**Optional**. It specifies the **confirm comment post by mail** setting,
establishing whether a comment confirmation should be sent by mail. If set
to ``True`` a confirmation message is sent to the user with a link on which
she has to click to confirm the comment. If the user is already authenticated
the confirmation is not sent and the comment is accepted, if no moderation has
been setup up,  with no further confirmation needed.

If is set to False, and no moderation has been set up to potentially discard
it, the comment will be accepted.

Read about the :ref:`moderation` topic in the tutorial.

An example::

     COMMENTS_XTD_CONFIRM_EMAIL = True

It defaults to ``True``.


.. setting:: COMMENTS_XTD_FROM_EMAIL

``COMMENTS_XTD_FROM_EMAIL``
===========================

**Optional**. It specifies the **from mail address** setting used in the
*from* field when sending emails.

An example::

     COMMENTS_XTD_FROM_EMAIL = "noreply@yoursite.com"

It defaults to ``settings.DEFAULT_FROM_EMAIL``.


.. setting:: COMMENTS_XTD_CONTACT_EMAIL

``COMMENTS_XTD_CONTACT_EMAIL``
==============================

**Optional. It specifies a **contact mail address** the user could use to get
in touch with a helpdesk or support personnel. It's used in both templates,
**email_confirmation_request.txt** and **email_confirmation_request.html**,
from the **templates/django_comments_xtd** directory.

An example::

     COMMENTS_XTD_FROM_EMAIL = "helpdesk@yoursite.com"

It defaults to ``settings.DEFAULT_FROM_EMAIL``.


.. setting:: COMMENTS_XTD_FORM_CLASS

``COMMENTS_XTD_FORM_CLASS``
===========================

**Optional**, form class to use when rendering comment forms. It's a string
with the class path to the form class that will be used for comments.

An example::

     COMMENTS_XTD_FORM_CLASS = "mycomments.forms.MyCommentForm"


It defaults to `"django_comments_xtd.forms.XtdCommentForm"`.


.. setting:: COMMENTS_XTD_MODEL

``COMMENTS_XTD_MODEL``
======================

**Optional**, represents the model class to use for comments. It's a string
with the class path to the model that will be used for comments.

An example::

     COMMENTS_XTD_MODEL = "mycomments.models.MyCommentModel"


Defaults to `"django_comments_xtd.models.XtdComment"`.


.. setting:: COMMENTS_XTD_LIST_ORDER

``COMMENTS_XTD_LIST_ORDER``
===========================

**Optional**, represents the field ordering in which comments are retrieve, a
tuple with field names, used by the ``get_queryset`` method of ``XtdComment``
model's manager.

It defaults to ``('thread_id', 'order')``
             

.. setting:: COMMENTS_XTD_MARKUP_FALLBACK_FILTER

``COMMENTS_XTD_MARKUP_FALLBACK_FILTER``
=======================================

**Optional**, default filter to use when rendering comments. Indicates the
default markup filter for comments. This value must be a key in the
:setting:`MARKUP_FILTER` setting. If not specified or None, comments that do
not indicate an intended markup filter are simply returned as plain text.

An example::

    COMMENTS_XTD_MARKUP_FALLBACK_FILTER = 'markdown'

It defaults to ``None``.


.. setting:: COMMENTS_XTD_SALT

``COMMENTS_XTD_SALT``
=====================

**Optional**, it is the **extra key to salt the comment form**. It establishes
the bytes string extra_key used by ``signed.dumps`` to salt the comment form
hash, so that there an additional secret is in use to encode the comment before
sending it for confirmation within a URL.

An example::

     COMMENTS_XTD_SALT = 'G0h5gt073h6gH4p25GS2g5AQ2Tm256yGt134tMP5TgCX$&HKOYRV'

It defaults to an empty string.


.. setting:: COMMENTS_XTD_SEND_HTML_EMAIL

``COMMENTS_XTD_SEND_HTML_EMAIL``
================================

**Optional**, enable/disable HTML mail messages. This boolean setting
establishes whether email messages have to be sent in HTML format. By the
default messages are sent in both Text and HTML format. By disabling the
setting, mail messages will be sent only in text format.

An example::

    COMMENTS_XTD_SEND_HTML_EMAIL = False

It defaults to True.


.. setting:: COMMENTS_XTD_THREADED_EMAILS

``COMMENTS_XTD_THREADED_EMAILS``
================================

**Optional**, enable/disable sending mails in separated threads. For low
traffic websites sending mails in separate threads is a fine solution.
However, for medium to high traffic websites such overhead could be reduced
by using other solutions, like a Celery application or any other detached
from the request-response HTTP loop.

An example::

    COMMENTS_XTD_THREADED_EMAILS = False

Defaults to ``True``.


.. setting:: COMMENTS_XTD_APP_MODEL_OPTIONS

``COMMENTS_XTD_APP_MODEL_OPTIONS``
==================================

**Optional**. Allow enabling/disabling commenting options on per
**app_label.model** basis. The options available are the following:

 * ``allow_flagging``: Allow registered users to flag comments as inappropriate.
 * ``allow_feedback``: Allow registered users to like/dislike comments.
 * ``show_feedback``: Allow django-comments-xtd to report the list of users who
   liked/disliked the comment. The representation of each user in the list
   depends on the next setting :setting::`COMMENTS_XTD_API_USER_REPR`.
 * ``who_can_post``: Can be either 'all' or 'users'. When it is 'all', all
   users can post, whether registered users or mere visitors. When it is
   'users', only registered users can post. Read the use case
   :ref:`ref-recipe-only-signed-in-can-comment`, for details on how to set it
   up.

An example use:

   .. code-block:: python

       COMMENTS_XTD_APP_MODEL_OPTIONS = {
           'blog.post': {
               'allow_flagging': True,
               'allow_feedback': True,
               'show_feedback': True,
               'who_can_post': 'users'
           }
       }

Defaults to:

   .. code-block:: python

       COMMENTS_XTD_APP_MODEL_OPTIONS = {
           'default': {
               'allow_flagging': False,
               'allow_feedback': False,
               'show_feedback': False,
               'who_can_post': 'all'
           }
       }

       
.. setting:: COMMENTS_XTD_API_USER_REPR

``COMMENTS_XTD_API_USER_REPR``
==============================

**Optional**. Function that receives a user object and returns its string
representation. It's used to produced the list of users who liked/disliked
comments. By default it outputs the username, but it could perfectly return the
full name:

   .. code-block:: python

       COMMENTS_XTD_API_USER_REPR = lambda u: u.get_full_name()

Defaults to:

   .. code-block:: python

       COMMENTS_XTD_API_USER_REPR = lambda u: u.username


.. setting:: COMMENTS_XTD_API_GET_USER_AVATAR

``COMMENTS_XTD_API_GET_USER_AVATAR``
====================================

.. _Gravatar: http://gravatar.com/

**Optional**. Path to the function used by the web API to retrieve the user's image URL of the user associated with a comment. By default django-comments-xtd tries to retrieve images from Gravatar_. If you use the web API (the JavaScript plugin uses it) then you might want to write a function to provide the URL to the user's image from a comment object. You might be interested on the use case :ref:`ref-change-user-image-or-avatar`, which cover the topic in depth. 

 .. code-block:: python

     COMMENTS_XTD_API_GET_USER_AVATAR = "comp.utils.get_avatar_url"

The function used by default, **get_user_avatar** in ``django_comments_xtd/utils.py``, tries to fetch every user's image from Gravatar:

 .. code-block:: python

     COMMENTS_XTD_API_GET_USER_AVATAR = "django_comments_xtd.utils.get_user_avatar"
