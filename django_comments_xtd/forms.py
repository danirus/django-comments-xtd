from django import forms
try:
    from django.apps import apps
except ImportError:
    from django.db.models.loading import cache as apps
from django.utils.translation import ugettext_lazy as _

try:
    from django_comments.forms import CommentForm
except ImportError:
    from django.contrib.comments.forms import CommentForm

from django_comments_xtd.conf import settings
from django_comments_xtd.models import TmpXtdComment


class XtdCommentForm(CommentForm):
    followup = forms.BooleanField(required=False,
                                  label=_("Notify me about follow-up comments"))
    reply_to = forms.IntegerField(required=True, initial=0,
                                  widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        comment = kwargs.pop("comment", None)
        if comment:
            initial = kwargs.pop("initial", {})
            initial.update({"reply_to": comment.pk})
            kwargs["initial"] = initial
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'placeholder': _('name')}))
        self.fields['email'] = forms.EmailField(
            label=_("Email"), help_text=_("Required for comment verification"),
            widget=forms.TextInput(attrs={'placeholder': _('email')})
            )
        self.fields['url'] = forms.URLField(
            required=False,
            widget=forms.TextInput(attrs={'placeholder': _('website')}))
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(attrs={'placeholder': _('comment')}),
            max_length=settings.COMMENT_MAX_LENGTH)

    def get_comment_model(self):
        return TmpXtdComment

    def get_comment_create_data(self):
        data = super(CommentForm, self).get_comment_create_data()
        ctype = data.get('content_type')
        object_pk = data.get('object_pk')
        model = apps.get_model(ctype.app_label, ctype.model)
        target = model._default_manager.get(pk=object_pk)
        data.update({'thread_id': 0, 'level': 0, 'order': 1,
                     'parent_id': self.cleaned_data['reply_to'],
                     'followup': self.cleaned_data['followup'],
                     'content_object': target})
        return data
