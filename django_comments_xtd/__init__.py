from django_comments_xtd.models import XtdComment
from django_comments_xtd.forms import XtdCommentForm

def get_model():
    return XtdComment

def get_form():
    return XtdCommentForm
