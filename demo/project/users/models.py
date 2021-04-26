from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that is used in "UserManager".
    """
    def _create_user(self, email, password, **extra_fields):
        """Creates and saves a User with the given email and password."""
        if not email:
            raise ValueError('The Email must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    name = models.CharField(_('name'), max_length=150, blank=True)
    url = models.URLField("url", blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)



CONFIRMATION_CHOICES = (
    ("B", "Blocked"),
    ("S", "Sign Up"),
    ("R", "Reset Pwd"),
    ("C", "Cancel Account"),
    ("E", "Change E-Mail"),
)

class Confirmation(models.Model):
    email = models.EmailField(unique=True)
    key = models.CharField(max_length=40, blank=False)
    creation_date = models.DateTimeField(
        "creation timestamp", default=datetime.now)
    purpose = models.CharField(max_length=1, choices=CONFIRMATION_CHOICES)
    notifications = models.SmallIntegerField(
        "notifications counter", default=0,
        help_text="homw many times has been notified")

    def __str__(self):
        if self.is_out_of_date():
            return (f"{self.email} (out of date, {self.notifications} "
                     "notifications).")
        else:
            return (f"{self.email} (still active, {self.notifications} "
                     "notifications).")

    def is_out_of_date(self):
        one_day = timedelta(days=1)
        now = timezone.now()
        diff =  now - self.creation_date
        if diff > one_day:
            return True
        else:
            return False
    is_out_of_date.short_description = "Out of date?"