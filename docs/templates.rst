.. _ref-templates:

=========
Templates
=========

This page details the list of templates provided by django-comments-xtd. They are located under the ``django_comments_xtd/`` templates directory.

.. contents:: Table of Contents
   :depth: 1
   :local:


.. index::
   single: email_confirmation_request
   pair: template; email_confirmation_request

``email_confirmation_request``
------------------------------
   
As ``.html`` and ``.txt``, this template represents the confirmation message sent to the user when the **Send** button is clicked to post a comment. Both templates are sent in a multipart message, or only in text format if the :setting:`COMMENTS_XTD_SEND_HTML_EMAIL` setting is set to ``False``.

In the context of the template the following objects are expected:

 * The ``site`` object (django-contrib-comments, and in turn django-comments-xtd, use the `Django Sites Framework <https://docs.djangoproject.com/en/1.11/ref/contrib/sites/>`_).
 * The ``comment`` object.
 * The ``confirmation_url`` the user has to click on to confirm the comment.


.. index::
   single: comment_tree
   pair: template; comment_tree

``comment_tree.html``
---------------------

This template is rendered by the :ref:`render-xtdcomment-tree` to represent the comments posted to an object.

In the context of the template the following objects are expected:

 * A list of dictionaries called ``comments`` in which each element is a dictionary like:

   .. code-block:: python

       {
           'comment': xtdcomment_object,
           'children': [ list_of_child_xtdcomment_dicts ]
       }
   
Optionally the following objects can be present in the template:

 * A boolean ``allow_flagging`` to indicate whether the user will have the capacity to suggest comment removal.
 * A boolean ``allow_feedback`` to indicate whether the user will have the capacity to like/dislike comments. When ``True`` the special template ``user_feedback.html`` will be rendered.


.. index::
   single: comment_tree
   pair: template; comment_tree
   
``user_feedback.html``
----------------------

This template is expected to be in the directory ``includes/django_comments_xtd/``, and it provides a way to customized the look of the like and dislike buttons as long as the list of users who clicked on them. It is included from ``comment_tree.html``. The template is rendered only when the :ref:`render-xtdcomment-tree` is used with the argument ``allow_feedback``.

In the context of the template is expected:

 * The boolean variable ``show_feedback``, which will be set to ``True`` when passing the argument ``show_feedback`` to the :ref:`render-xtdcomment-tree`. If ``True`` the template will show the list of users who liked the comment and the list of those who disliked it.
 * A comment ``item``.

Look at the section :ref:`show-the-list-of-users` to read on this particular topic.


.. index::
   single: liked
   pair: template; liked

``like.html``
--------------

This template is rendered when the user clicks on the **like** button of a comment.

The context of the template expects:

 * A boolean ``already_liked_it`` that indicates whether the user already clicked on the like button of this comment. In such a case, if the user submits the form a second time the liked-it flag is withdrawn.
 * The ``comment`` subject to be liked.


.. index::
   single: liked
   pair: template; liked

``liked.html``
--------------

This template is rendered when the user click on the submit button of the form presented in the ``like.html`` template. The template is meant to thank the user for the feedback. The context for the template doesn't expect any specific object.
   

.. index::
   single: liked
   pair: template; liked

``dislike.html``
----------------

This template is rendered when the user clicks on the **dislike** button of a comment.

The context of the template expects:

 * A boolean ``already_disliked_it`` that indicates whether the user already clicked on the dislike button for this comment. In such a case, if the user submits the form a second time the disliked-it flag is withdrawn.
 * The ``comment`` subject to be liked.


.. index::
   single: liked
   pair: template; liked

``disliked.html``
-----------------

This template is rendered when the user click on the submit button of the form presented in the ``dislike.html`` template. The template is meant to thank the user for the feedback. The context for the template doesn't expect any specific object.


.. index::
   single: discarded
   pair: template; discarded

``discarded.html``
------------------

This template gets rendered if any receiver of the signal ``confirmation_received`` returns ``False``. Informs the user that the comment has been discarded. Read the subsection :ref:`signal-and-receiver-label` in the **Control Logic** to know about the ``confirmation_received`` signal.


.. index::
   single: email_followup_comment
   pair: template; email_followup_comment

``email_followup_comment``
--------------------------

As ``.html`` and ``.txt``, this template represents the mail message sent to notify that comments have been sent after yours. It's sent to the user who posted the comment in the first place, when another comment arrives in the same thread or in a not nested list of comments. To receive this email the user must tick the box *Notify me follow up comments via email*.

The template expects the following objects in the context:

 * The ``site`` object.
 * The ``comment`` object about which users are being informed.
 * The ``mute_url`` to offer the notified user the chance to stop receiving notifications on new comments.


.. index::
   single: ajax
   pair: template; ajax

``comment.html``
----------------

This template is rendered under any of the following circumstances:

 * When using the :ref:`render-last-xtdcomments`.
 * When a logged in user sends a comment via Ajax. The comment gets rendered immediately. JavaScript client side code still has toe handle the response.


.. index::
   single: posted
   pair: template; posted

``posted.html``
---------------

Rendered when a not authenticated user sends a comment. It informs the user that a confirmation message has been sent and that the link contained in the mail must be clicked to confirm the publication of the comment.


.. index::
   single: reply
   pair: template; reply

``reply.html``
--------------

Rendered when a user clicks on the **reply** link of a comment. Reply links are created with ``XtdComment.get_reply_url`` method. They show up below the text of each comment when they allow nested comments.

.. index::
   single: muted
   pair: template; muted

``muted.html``
--------------

Rendered when a user clicks on the **mute link** received in a follow-up notification message. It informs the user that the site will not send more notifications on new comments sent to the object.


``only_users_can_post.html``
----------------------------

django-comments-xtd can be customize so that only registered users can post comments. Read the use case *Only registered users can post*, for details. The purpose of this template is to allow customizing the HTML message displayed when a non-registered visitor gets to the comments page. The message is displayed instead of the comment form.

This template expects a context variable ``html_id_suffix``.