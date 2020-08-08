from __future__ import unicode_literals
from django.conf import settings


COMMENT_MAX_LENGTH = 3000

# Extra key to salt the XtdCommentForm.
COMMENTS_XTD_SALT = b""

# Whether comment posts should be confirmed by email.
COMMENTS_XTD_CONFIRM_EMAIL = True

# From email address.
COMMENTS_XTD_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

# Contact email address.
COMMENTS_XTD_CONTACT_EMAIL = settings.DEFAULT_FROM_EMAIL

# Maximum Thread Level.
COMMENTS_XTD_MAX_THREAD_LEVEL = 0

# Maximum Thread Level per app.model basis.
COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {}

# Default order to list comments in.
COMMENTS_XTD_LIST_ORDER = ('thread_id', 'order')

# Form class to use.
COMMENTS_XTD_FORM_CLASS = "django_comments_xtd.forms.XtdCommentForm"

# Model to use.
COMMENTS_XTD_MODEL = "django_comments_xtd.models.XtdComment"

# Send HTML emails.
COMMENTS_XTD_SEND_HTML_EMAIL = True

# Whether to send emails in separate threads or use the regular method.
# Set it to False to use a third-party app like django-celery-email or
# your own celery app.
COMMENTS_XTD_THREADED_EMAILS = True

# Define what commenting features a pair app_label.model can have.
COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'who_can_post': 'all',  # Valid values: "users", "all"
        'allow_flagging': False,
        'allow_feedback': False,
        'show_feedback': False,
    }
}


# Define a function to return the user representation. Used by
# the web API to represent user strings in response objects.
def username(u):
    return u.username


COMMENTS_XTD_API_USER_REPR = username


# Function to obtain comment's avatar. Receives the comment as a parameter.
# Rewrite this function to make the web API use a different logic.
# Should return an URL.
COMMENTS_XTD_API_GET_USER_AVATAR = "django_comments_xtd.utils.get_user_avatar"
