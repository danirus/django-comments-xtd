"""
Signals relating to django-comments-xtd.
"""
from django.dispatch import Signal

# Sent just after a comment has been verified.
confirmation_received = Signal(providing_args=["comment", "request"])

# Sent just after a user has muted a comments thread.
comment_thread_muted = Signal(providing_args=["comment", "requests"])
