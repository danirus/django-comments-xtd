.. _ref-templates:

=========
Templates
=========

List of template files coming with Django-comments-xtd.

**django_comments_xtd/email_confirmation_request.(html|txt)**
    Comment confirmation email sent to the user when she clicks on "Post" to send the comment. The user should click on the link in the message to confirm the comment. If the user is authenticated the message is not sent, as the comment is directly approved.

**django_comments_xtd/confirmation_requested.html**
    Rendered right after the comment confirmation email has been sent. Informs the user about the confirmation email and request her to click on the link to confirm the comment.

**django_comments_xtd/discarded.html**
    Rendered if any receiver of the signal ``confirmation_received`` returns False. Tells the user the comment has been discarded.

**django_comments_xtd/email_followup_comment.(html|txt)**
    Email message sent when there is a new comment following up the user's. To receive this email the user must tick the box *Notify me of follow up comments via email*.

