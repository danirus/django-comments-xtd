from django import forms
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.models import TmpXtdComment


class MyCommentForm(XtdCommentForm):
    title = forms.CharField(max_length=256,
                            widget=forms.TextInput(
                                attrs={'placeholder': _('title'),
                                       'class': 'form-control'}))
    
    def get_comment_create_data(self, site_id=None):
        data = super(MyCommentForm, self).get_comment_create_data()
        data.update({'title': self.cleaned_data['title']})
        return data
