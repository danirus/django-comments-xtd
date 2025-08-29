import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _

from .models import Confirmation, User

MIN_NAME_LEN = 5
MIN_PASSWORD_LEN = 8

MAX_CONFIRMATION_NOTIFICATIONS = 3

# ---------------------------------------------------------------------
# Login form.

confirm_pending_msg = _(
    "Your registration process is not finished yet, you  have to confirm your e-Mail address. Check the e-Mail message we already sent you."
)
usr_not_active_msg = _("This user account is not active.")
usr_not_auth_msg = _(
    "Enter a correct e-Mail address and password. Note that both fields are case-sensitive."
)


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"tabindex": 1})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"tabindex": 2})
    )
    remember = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"tabindex": 3}),
        label=_("Remember me"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(self.request, email=email, password=password)
            if not user:
                raise forms.ValidationError(usr_not_auth_msg)
            else:
                self.user = user
                try:
                    confirmation = Confirmation.objects.get(email=email)
                except Confirmation.DoesNotExist as exc:
                    if not user.is_active:
                        raise forms.ValidationError(usr_not_active_msg) from exc
                else:
                    if not user.is_active:
                        raise forms.ValidationError(confirm_pending_msg)
                    else:
                        confirmation.delete()

        return self.cleaned_data


# ---------------------------------------------------------------------
# Register forms:
# * 1st step: Provide email, name and URL: RegisterStep1Form.
# * ... Once email is confirmed  ...
# * 2nd step: Provide a password for your account: CreatePwdStep2Form.
#
# Reset password forms:
# * 1st step: Provide email: ResetPwdStep1Form.
# * ... Once email is confirmed ...
# * 2nd step: Provide a password for your account: CreatePwdStep2Form.

class RegisterStep1Form(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"tabindex": 1}))
    name = forms.CharField(
        label=_("Name"),
        max_length=150,
        widget=forms.TextInput(attrs={"size": 30, "tabindex": 2}),
    )
    url = forms.URLField(
        required=False,
        label=_("Personal URL"),
        widget=forms.URLInput(attrs={"tabindex": 3, "autocomplete": "off"}),
    )

    def clean_email(self):
        if "email" in self.cleaned_data:
            email = self.cleaned_data["email"].lower()
            try:
                get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return email
            else:
                raise forms.ValidationError(
                    _("This E-Mail address is already registered.")
                )

    def clean_name(self):
        if "name" in self.cleaned_data:
            if (
                re.search(r"^[\W]+", self.cleaned_data["name"]) is not None
                or len(self.cleaned_data["name"]) < MIN_NAME_LEN
            ):
                raise forms.ValidationError(
                    _(f"Please, provide a name with at least {MIN_NAME_LEN} characters.")
                )
            return self.cleaned_data["name"]


class ResetPwdStep1Form(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"tabindex": 1}))


class SetPwdStep2Form(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    pwd1 = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={"tabindex": 1}),
        label=_("Type a New Password"),
    )
    pwd2 = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={"tabindex": 2}),
        label=_("Confirm the Password"),
    )

    def clean(self):
        pwd1 = self.cleaned_data.get("pwd1")
        pwd2 = self.cleaned_data.get("pwd2")

        if pwd1 and pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError(
                    _("Please, type the same password in both fields.")
                )

            if len(pwd1) < MIN_PASSWORD_LEN:
                raise forms.ValidationError(
                    _(
                        "Please, provide a password longer than "
                        f"{MIN_PASSWORD_LEN} characters."
                    )
                )

            return self.cleaned_data


# ---------------------------------------------------------------------
# Change email address form.

email_already_registered = "This e-Mail address is already registered."
too_many_attempts = (
    "Please, wait 24 hours to request another email address change."
)
profile_did_not_change = "Data did not change."


class ProfileForm(forms.Form):
    email = forms.CharField(required=True)
    name = forms.CharField(max_length=150, required=False, label=_("Name"))
    url = forms.URLField(required=False, label=_("Personal URL"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        if self.user:
            kwargs["initial"] = {
                "email": self.user.email,
                "name": self.user.name,
                "url": self.user.url,
            }
        super().__init__(*args, **kwargs)

    def clean_email(self):
        # Check if strip is necessary.
        email = self.cleaned_data["email"].strip()
        if self.user and self.user.email == email:
            return email

        try:
            if User.objects.filter(email=email).count():
                raise forms.ValidationError(email_already_registered)

            # If there is already an email change confirmation
            # for this user, the update the confirmation.
            confirm = Confirmation.objects.get(email=self.user.email)
            if (
                not confirm.is_out_of_date()
                and confirm.notifications < MAX_CONFIRMATION_NOTIFICATIONS
            ):
                confirm.key = email
                confirm.notifications += 1
                confirm.save()
                return email

            elif confirm.is_out_of_date():
                confirm.delete()
                Confirmation.objects.create(
                    email=self.user.email, key=email, purpose="E"
                )  # Change email.
                return email

            else:
                raise forms.ValidationError(too_many_attempts)

        except Confirmation.DoesNotExist:
            Confirmation.objects.create(
                email=self.user.email, key=email, purpose="E"
            )  # Change email.
            return email

    def clean(self):
        email = self.cleaned_data["email"].strip()
        name = self.cleaned_data["name"].strip()
        url = self.cleaned_data["url"].strip()

        if (
            self.user
            and email == self.user.email
            and name == self.user.name
            and url == self.user.url
        ):
            raise forms.ValidationError(profile_did_not_change)

        return self.cleaned_data


# --------------------------------------------------------------------
# Change password form.


class ResetPwdForm(forms.Form):
    """Reset Password Form."""

    pwd1 = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={"tabindex": 1}),
        label=_("Type a New Password"),
    )
    pwd2 = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={"tabindex": 2}),
        label=_("Confirm the Password"),
    )

    def clean(self):
        pwd1 = self.cleaned_data.get("pwd1")
        pwd2 = self.cleaned_data.get("pwd2")

        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError(
                _("Please, type the same password in both fields.")
            )
        return self.cleaned_data


# ---------------------------------------------------------------------
# Change password form.


ANONYMIZE_CHOICES = (
    ("Y", _("Anonymize my contributions.")),
    ("N", _("Keep my name in my contributions.")),
)


class CancelForm(forms.Form):
    """Account cancelation Form."""

    anonymize = forms.ChoiceField(
        choices=ANONYMIZE_CHOICES,
        initial="Y",
        widget=forms.RadioSelect(),
        label=_("About my contributions"),
    )
    cancel = forms.BooleanField(
        label=_("Yes, I want to cancel my account."), required=False
    )

    def clean_cancel(self):
        if not self.cleaned_data["cancel"]:
            raise forms.ValidationError(
                _("You must confirm that you want to cancel your account")
            )
        return self.cleaned_data["cancel"]
