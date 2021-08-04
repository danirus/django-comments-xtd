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

# Enum class for comment reactions.
COMMENTS_XTD_REACTIONS_ENUM = "django_comments_xtd.models.ReactionEnum"

# Send HTML emails.
COMMENTS_XTD_SEND_HTML_EMAIL = True

# Whether to send emails in separate threads or use the regular method.
# Set it to False to use a third-party app like django-celery-email or
# your own celery app.
COMMENTS_XTD_THREADED_EMAILS = True

# Define what commenting features a pair app_label.model can have.
COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'who_can_post': 'all',  # Valid values: "users", "all",
        # Function to determine whether new comments,
        # reactions, etc. should be allowed for a given object.
        'check_input_allowed': 'django_comments_xtd.utils.check_input_allowed',

        # Whether to display a link to flag a comment as inappropriate.
        'comment_flagging_enabled': False,

        # Whether to allow users to submit reactions on comments.
        'comment_reactions_enabled': False,

        # Whether to allow users to submit reactions on any object
        # registered as a content type.
        'object_reactions_enabled': False
    }
}

# When True, an approval or removal operation on a comment will
# trigger a publishing or withholding operation on its nested comments.
COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED = True


# Define a function to return the user representation. Used by
# the web API to represent user strings in response objects.
def username(u):
    return u.username


COMMENTS_XTD_API_USER_REPR = username


# Makes the "Notify me about followup comments" checkbox in the
# comment form checked (True) or unchecked (False) by default.
COMMENTS_XTD_DEFAULT_FOLLOWUP = False

# How many reaction buttons can be displayed
# in a row before it breaks into another row.
COMMENTS_XTD_REACTIONS_ROW_LENGTH = 4

# Display up to the given number of comments in the last page to avoid
# creating another page containing only these amount of comments.
COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS = 10

# Number of comments per page. When <=0 pagination is disabled.
COMMENTS_XTD_ITEMS_PER_PAGE = 25

# Name of the query string parameter containing the page number.
COMMENTS_XTD_PAGE_QUERY_STRING_PARAM = "cpage"