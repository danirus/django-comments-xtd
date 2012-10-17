from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd.models import TmpXtdComment


COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)
CONFIRM_EMAIL = getattr(settings,'COMMENTS_XTD_CONFIRM_EMAIL', True)
MAX_THREAD_LEVEL = getattr(settings, 'COMMENTS_XTD_MAX_THREAD_LEVEL', 0)

class XtdCommentForm(CommentForm):
    followup = forms.BooleanField(
        required=False, label=_("Notify me of follow up comments via email"))
    reply_to = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        comment = kwargs.pop("comment", None)
        if comment:
            initial = kwargs.pop("initial", {})
            initial.update({"reply_to": comment.pk})
            kwargs["initial"] = initial
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            label=_("Email address"), help_text=_("Required for comment verification"))
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(attrs={'placeholder':_('your comment')}), 
            max_length=COMMENT_MAX_LENGTH)

    def get_comment_model(self):
        return TmpXtdComment

    def get_comment_create_data(self):
        data = super(CommentForm, self).get_comment_create_data()
        data.update({'thread_id': 0, 'level': 0, 'order': 1,
                     'parent_id': self.cleaned_data['reply_to'],
                     'followup': self.cleaned_data['followup']})
        if CONFIRM_EMAIL:
            # comment must be verified before getting approved
            data['is_public'] = False
        return data
