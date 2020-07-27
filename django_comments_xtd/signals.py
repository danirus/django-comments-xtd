"""
Signals relating to django-comments-xtd.
"""
from django.dispatch import Signal

# Sent just after a comment has been verified.
confirmation_received = Signal(providing_args=["comment", "request"])

# Sent just after a user has muted a comments thread.
comment_thread_muted = Signal(providing_args=["comment", "request"])

# Sent before the data in the REST POST comment form is validated.
# A receiver returning True will suffice to automatically add valid values
# to the CommentSecurityForm fields 'timestamp' and 'security_hash'. The
# intention is to combine a receiver with a django-rest-framework
# authentication class, and return True when the request.auth is not None.
should_request_be_authorized = Signal(providing_args=["comment", "request"])
