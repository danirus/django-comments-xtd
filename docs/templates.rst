.. _ref-templates:

=========
Templates
=========

List of template files coming with Django-comments-xtd.

.. index::
   single: email_confirmation_request
   pair: template; email_confirmation_request

**django_comments_xtd/email_confirmation_request.(html|txt)**
    Comment confirmation email sent to the user when she clicks on "Post" to send the comment. The user should click on the link in the message to confirm the comment. If the user is authenticated the message is not sent, as the comment is directly approved.

.. index::
   single: discarded
   pair: template; discarded

**django_comments_xtd/discarded.html**
    Rendered if any receiver of the signal ``confirmation_received`` returns False. Tells the user the comment has been discarded.

.. index::
   single: email_followup_comment
   pair: template; email_followup_comment

**django_comments_xtd/email_followup_comment.(html|txt)**
    Email message sent when there is a new comment following up the user's. To receive this email the user must tick the box *Notify me of follow up comments via email*.
