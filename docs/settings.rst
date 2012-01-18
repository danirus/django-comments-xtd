.. _ref-settings:

========
Settings
========

In order to use Django-comments-xtd it is required to declare the setting `COMMENTS_APP <https://docs.djangoproject.com/en/1.3/ref/contrib/comments/settings/#std:setting-COMMENTS_APP>`_::

    COMMENTS_APP = "django_comments_xtd"

Additionally, Django-comments-xtd's behaviour may change depending on the following two settings.


``COMMENTS_XTD_CONFIRM_EMAIL``
==============================

**Optional**

This setting establishes whether a comment confirmation should be sent by email. If set to True a confirmation message is sent to the user with a link she has to click on. If the user is already authenticated the confirmation is not sent.

If is set to False the comment is accepted (unless your discard it by returning False when receiving the signal ``comment_will_be_posted``, defined by the Django Comments Framework).

An example::

     COMMENTS_XTD_CONFIRM_EMAIL = True

Defaults to True.


``COMMENTS_XTD_SALT``
=====================

**Optional**

This setting establishes the ASCII string extra_key used by ``signed.dumps`` to salt the contact form hash. As ``signed.dumps`` docstring says, just in case you're worried that the NSA might try to brute-force your SHA-1 protected secret.

An example::

     COMMENTS_XTD_SALT = 'G0h5gt073h6gH4p25GS2g5AQ25hTm256yGt134tMP5TgCX$&HKOYRV'

Defaults to an empty string.
