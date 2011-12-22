from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd.models import TmpXtdComment

class XtdCommentForm(CommentForm):
    followup = forms.BooleanField(
        required=False, label=_("Notify me of follow up comments via email"))

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            label=_("Email address"), help_text=_("Required for comment verification"))

    def get_comment_model(self):
        return TmpXtdComment

    def get_comment_create_data(self):
        data = super(CommentForm, self).get_comment_create_data()
        data['followup'] = self.cleaned_data['followup']
        if settings.COMMENTS_XTD_CONFIRM_EMAIL:
            # comment must be verified before getting approved
            data['is_public'] = False
        return data
