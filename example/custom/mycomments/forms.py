from django import forms
from django.utils.translation import gettext_lazy as _

from django_comments_xtd.forms import XtdCommentForm


class MyCommentForm(XtdCommentForm):
    title = forms.CharField(
        max_length=256,
        widget=forms.TextInput(
            attrs={"placeholder": _("title"), "class": "form-control"}
        ),
    )

    def get_comment_create_data(self, site_id=None):
        data = super().get_comment_create_data()
        data.update({"title": self.cleaned_data["title"]})
        return data
