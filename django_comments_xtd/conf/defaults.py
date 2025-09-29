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

# By default ContentType.objects.get_for_model pass True in the
# keyword argument `for_concrete_model`. If you use Proxy models
# you might want to make django-comments-xtd use the proxy models
# instead. In such a case switch this setting to False.
COMMENTS_XTD_FOR_CONCRETE_MODEL = True

# Default order to list comments in.
COMMENTS_XTD_LIST_ORDER = ("thread__id", "order")

# Form class to use.
COMMENTS_XTD_FORM_CLASS = "django_comments_xtd.forms.XtdCommentForm"

# Model to use.
COMMENTS_XTD_MODEL = "django_comments_xtd.models.XtdComment"

# Enum class for comment reactions.
COMMENTS_XTD_REACTION_ENUM = "django_comments_xtd.models.ReactionEnum"

# Send HTML emails.
COMMENTS_XTD_SEND_HTML_EMAIL = True

# Whether to send emails in separate threads or use the regular method.
# Set it to False to use a third-party app like django-celery-email or
# your own celery app.
COMMENTS_XTD_THREADED_EMAILS = True

# Define what commenting features a pair app_label.model can have.
COMMENTS_XTD_APP_MODEL_CONFIG = {
    "default": {
        "who_can_post": "all",  # Valid values: "users", "all".
        # Function to determine whether new comments, reactions, etc.
        # should be allowed for a given object.
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        # Whether to display a link to flag comments as inappropriate.
        "comments_flagging_enabled": False,
        # Whether to allow users to submit reactions on comments.
        # Default reactions are +1/-1. They can be customize. See
        # example projects.
        "comments_reacting_enabled": False,
        # Whether to allow users to vote on comments.
        "comments_voting_enabled": False,
        # Default order to list comments.
        "list_order": ("thread__id", "order"),
    }
}


# Define a function to return the user representation.
def _get_username(user):
    return user.username


COMMENTS_XTD_FN_USER_REPR = _get_username

# Makes the "Notify me about followup comments" checkbox in the
# comment form checked (True) or unchecked (False) by default.
COMMENTS_XTD_DEFAULT_FOLLOWUP = False

# How many reaction buttons can be displayed
# in a row before it breaks into another row.
COMMENTS_XTD_REACTIONS_ROW_LENGTH = 4

# How many users are listed when hovering a reaction.
COMMENTS_XTD_MAX_USERS_IN_TOOLTIP = 10

# Use a theme by assigning a value to the COMMENTS_INK_THEME setting.
# The value must be the name of a directory within the templates directory.
# By default django-comments-xtd comes with a few themes that you can use
# to render comments. Create your own themed templates by adding a new
# theme directory to your project template's directory under
# `comments/themes/<your-theme>`.
# Provided themes: avatar_in_thread, avatar_in_header, feedback_in_header.
COMMENTS_XTD_THEME = ""

# Python path to the object defining the paths to your templates.
COMMENTS_XTD_TEMPLATE_PATTERNS: str = (
    "django_comments_xtd.templating.template_patterns"
)

# How many users to list per page, when displaying the
# users that selected the same comment reaction, in the
# `django_comments_xtd.views.CommentReactionUserListView`.
COMMENTS_XTD_NUM_COMMENT_REACTION_USERS_PER_PAGE = 30

# Tuple of fields to establish the order to list the users
# that selected the same comment reaction.
COMMENTS_XTD_COMMENT_REACTION_USERS_ORDER: tuple = ("-id",)
