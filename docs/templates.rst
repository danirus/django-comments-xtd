.. _ref-templates:

=========
Templates
=========

List of template files used by django-comments-xtd.

.. index::
   single: email_confirmation_request
   pair: template; email_confirmation_request

**django_comments_xtd/email_confirmation_request.(html|txt)** (included)
    Comment confirmation email sent to the user when she clicks on "Post" to send the comment. The user should click on the link in the message to confirm the comment. If the user is authenticated the message is not sent, as the comment is directly approved.

.. index::
   single: discarded
   pair: template; discarded

**django_comments_xtd/discarded.html** (included)
    Rendered if any receiver of the signal ``confirmation_received`` returns False. Tells the user the comment has been discarded.

.. index::
   single: email_followup_comment
   pair: template; email_followup_comment

**django_comments_xtd/email_followup_comment.(html|txt)** (included)
    Email message sent when there is a new comment following up the user's. To receive this email the user must tick the box *Notify me of follow up comments via email*.

.. index::
   single: max_thread_level
   pair: template; max_thread_level

**django_comments_xtd/max_thread_level.html** (included)
    Rendered when a nested comment is sent with a thread level over the maximum thread level allowed. The template in charge of rendering the list of comments can make use of ``comment.allow_thread`` (True when the comment accepts nested comments) to avoid adding the link "Reply" on comments that don't accept nested comments. See the simple_threads demo site, template ``comment/list.html`` to see a use example of ``comment.allow_thread``.

.. index::
   single: ajax
   pair: template; ajax

**django_comments_xtd/comment.html** (included)
    Rendered when a logged in user sent a comment via Ajax. The comment gets rendered immediately. JavaScript client side code still has to handle the response.

.. index::
   single: posted
   pair: template; posted

**django_comments_xtd/posted.html**
    Rendered when a not logged-in user sends a comment. Django-comments-xtd try first to find the template in its own template directory, ``django_comments_xtd/posted.html``. If it doesn't exist, it will use the template in Django Comments Framework directory: ``comments/posted.html``. Look at the demo sites for sample uses.

.. index::
   single: reply
   pair: template; reply

**django_comments_xtd/reply.html** (included)
    Rendered when a user clicks on the *reply* link of a comment. Reply links are created with ``XtdComment.get_reply_url`` method.

.. index::
   single: muted
   pair: template; muted

**django_comments_xtd/muted.html** (included)
    Rendered when a user clicks on the *mute link* of a follow-up email message.
