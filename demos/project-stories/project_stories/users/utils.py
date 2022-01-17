from django.conf import settings
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext as _

from django_comments_xtd.utils import send_mail


def notify_emailaddr_change_confirmation(
    key, user, email, site,
    text_template="users/emailaddr_change_confirmation.txt",
    html_template="users/emailaddr_change_confirmation.html"
):
    """Send email requesting email-address change confirmation."""
    subject = _("Request to change your account's email address")
    confirmation_url = reverse("change-email-confirm",
                               args=[key.decode('utf-8')])
    message_context = {'user': user,
                       'new_email': email,
                       'confirmation_url': confirmation_url,
                       'contact': settings.COMMENTS_XTD_FROM_EMAIL,
                       'site': site}
    # Prepare text message.
    text_message_template = loader.get_template(text_template)
    text_message = text_message_template.render(message_context)
    if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
        # prepare html message
        html_message_template = loader.get_template(html_template)
        html_message = html_message_template.render(message_context)
    else:
        html_message = None

    send_mail(subject, text_message, settings.COMMENTS_XTD_FROM_EMAIL,
              [email,], html=html_message)


def send_confirm_user_registration_request(
    form, key, site,
    text_tmpl="users/user_registration_confirmation.txt",
    html_tmpl="users/user_registration_confirmation.html"
):
    subject = _("confirm registration request")
    confirmation_url = reverse("register-confirm", args=[key.decode('utf-8')])
    context = {'name': form.cleaned_data['name'],
               'email': form.cleaned_data['email'],
               'confirmation_url': confirmation_url,
               'contact': settings.COMMENTS_XTD_CONTACT_EMAIL,
               'site': site}
    return send_confirmation_request(subject, context, text_tmpl, html_tmpl)


def send_confirm_account_deletion_request(
    user, key, site,
    text_tmpl="users/account_deletion_confirmation.txt",
    html_tmpl="users/account_deletion_confirmation.html"
):
    subject = _("confirm account deletion request")
    confirmation_url = reverse("delete-confirm", args=[key.decode('utf-8')])
    context = {'name': user.name,
               'email': user.email,
               'confirmation_url': confirmation_url,
               'contact': settings.COMMENTS_XTD_CONTACT_EMAIL,
               'site': site}
    return send_confirmation_request(subject, context, text_tmpl, html_tmpl)


def send_confirmation_request(subject, context, text_tmpl, html_tmpl):
    """Send email requesting user confirmation."""
    text_message_template = loader.get_template(text_tmpl)
    text_message = text_message_template.render(context)

    if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
        # prepare html message
        html_message_template = loader.get_template(html_tmpl)
        html_message = html_message_template.render(context)
    else:
        html_message = None

    send_mail(subject, text_message, settings.COMMENTS_XTD_FROM_EMAIL,
              [context['email'], ], html=html_message)


