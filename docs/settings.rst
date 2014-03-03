.. _ref-settings:

========
Settings
========

In order to use Django-comments-xtd it is required to declare the setting `COMMENTS_APP <https://docs.djangoproject.com/en/1.3/ref/contrib/comments/settings/#std:setting-COMMENTS_APP>`_::

    COMMENTS_APP = "django_comments_xtd"

Additionally, Django-comments-xtd's behaviour may change depending on the following two settings.


Maximum Thread Level
====================

:index:`COMMENTS_XTD_MAX_THREAD_LEVEL` - Maximum Thread Level

**Optional**

Indicate the maximum thread level for comments. 

An example::

     COMMENTS_XTD_MAX_THREAD_LEVEL = 8

Defaults to 0. What means threads are not permitted.
 

Maximum Thread Level per App.Model
==================================

:index:`COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL` - Maximum Thread Level per app.model basis

**Optional**

A dictionary with `app_label.model` as keys and the maximum thread level for comments posted to instances of those models as values. It allows definition of max comment thread level on a per `app_label.model` basis.

An example::

    COMMENTS_XTD_MAX_THREAD_LEVEL = 0
    COMMENTS_XTD_MAX_THREAD_LEVEL_BY_MODEL = {
        'projects.release': 2,
	'blog.stories': 8, 'blog.quotes': 8, 
	'blog.diarydetail': 0 # not required as it defaults to COMMENTS_XTD_MAX_THREAD_LEVEL
    }


Confirm Comment Post by Email
=============================

:index:`COMMENTS_XTD_CONFIRM_EMAIL` - Confirm Comment Post by Email

**Optional**

This setting establishes whether a comment confirmation should be sent by email. If set to True a confirmation message is sent to the user with a link she has to click on. If the user is already authenticated the confirmation is not sent.

If is set to False the comment is accepted (unless your discard it by returning False when receiving the signal ``comment_will_be_posted``, defined by the Django Comments Framework).

An example::

     COMMENTS_XTD_CONFIRM_EMAIL = True

Defaults to True.


Comment Form Class
=============

:index:`COMMENTS_XTD_FORM_CLASS` - Form class to use when rendering comment forms.

**Optional**

A classpath to the form class that will be used for comments.

An example::

     COMMENTS_XTD_FORM_CLASS = "mycomments.forms.MyCommentForm"


Defaults to `"django_comments_xtd.forms.XtdCommentForm"`.


Comment Model
=============

:index:`COMMENTS_XTD_MODEL` - Model to use

**Optional**

A classpath to the model that will be used for comments.

An example::

     COMMENTS_XTD_MODEL = "mycomments.models.MyCommentModel"


Defaults to `"django_comments_xtd.models.XtdComment"`.


Salt
====

:index:`COMMENTS_XTD_SALT` - Extra key to salt the form

**Optional**

This setting establishes the ASCII string extra_key used by ``signed.dumps`` to salt the comment form hash. As ``signed.dumps`` docstring says, just in case you're worried that the NSA might try to brute-force your SHA-1 protected secret.

An example::

     COMMENTS_XTD_SALT = 'G0h5gt073h6gH4p25GS2g5AQ25hTm256yGt134tMP5TgCX$&HKOYRV'

Defaults to an empty string.
