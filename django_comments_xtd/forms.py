from django import forms
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_comments.forms import CommentForm

from django_comments_xtd.conf import settings
from django_comments_xtd.models import TmpXtdComment


class XtdCommentForm(CommentForm):
    followup = forms.BooleanField(
        required=False, label=_("Notify me about follow-up comments")
    )
    reply_to = forms.IntegerField(
        required=True, initial=0, widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        comment = kwargs.pop("comment", None)
        if comment:
            initial = kwargs.pop("initial", {})
            initial.update({"reply_to": comment.pk})
            kwargs["initial"] = initial
            followup_suffix = f"_{comment.pk}"
        else:
            followup_suffix = ""

        super(CommentForm, self).__init__(*args, **kwargs)

        self.fields["name"].label = _("Name")
        self.fields["name"].widget = forms.TextInput(
            attrs={"placeholder": _("name")}
        )

        self.fields["email"].label = _("Mail")
        self.fields["email"].help_text = _("Required for comment verification")
        self.fields["email"].widget = forms.TextInput(
            attrs={"placeholder": _("mail address")}
        )

        self.fields["url"].label = _("Link")
        self.fields["url"].required = False
        self.fields["url"].widget = forms.TextInput(
            attrs={
                "placeholder": _("url your name links to (optional)"),
            }
        )

        self.fields["comment"].widget = forms.Textarea(
            attrs={"placeholder": _("Your comment"),}
        )
        self.fields["comment"].max_length = settings.COMMENT_MAX_LENGTH
        self.fields["comment"].widget.attrs.pop("cols")
        self.fields["comment"].widget.attrs.pop("rows")

        self.fields["followup"].widget.attrs[
            "id"
        ] = f"id_followup{followup_suffix}"
        self.fields["followup"].initial = settings.COMMENTS_XTD_DEFAULT_FOLLOWUP

    def get_comment_model(self):
        return TmpXtdComment

    def get_comment_create_data(self, site_id=None):
        data = {
            "content_type": ContentType.objects.get_for_model(
                self.target_object,
                for_concrete_model=settings.COMMENTS_XTD_FOR_CONCRETE_MODEL
            ),
            "object_pk": force_str(self.target_object._get_pk_val()),
            "user_name": self.cleaned_data["name"],
            "user_email": self.cleaned_data["email"],
            "user_url": self.cleaned_data["url"],
            "comment": self.cleaned_data["comment"],
            "submit_date": timezone.now(),
            "site_id": site_id or getattr(settings, "SITE_ID", None),
            "is_public": True,
            "is_removed": False,
        }
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        model = apps.get_model(ctype.app_label, ctype.model)
        target = model._default_manager.get(pk=object_pk)
        data.update(
            {
                "level": 0,
                "order": 1,
                "parent_id": self.cleaned_data["reply_to"],
                "followup": self.cleaned_data["followup"],
                "content_object": target,
            }
        )
        return data
