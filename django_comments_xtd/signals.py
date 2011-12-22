"""
Signals relating to django-comments-xtd.
"""
from django.dispatch import Signal

# Sent just after a comment has been verified.
confirmation_received = Signal(providing_args=["comment", "request"])

