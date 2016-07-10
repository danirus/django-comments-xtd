# Idea borrowed from Selwin Ong post:
# http://ui.co.id/blog/asynchronous-send_mail-in-django

try:
    import Queue as queue  # python2
except ImportError:
    import queue as queue  # python3

import threading
from django.core.mail import EmailMultiAlternatives
from django_comments_xtd.conf import settings


mail_sent_queue = queue.Queue()


class EmailThread(threading.Thread):
    def __init__(self, subject, body, from_email, recipient_list,
                 fail_silently, html):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        _send_mail(self.subject, self.body, self.from_email,
                   self.recipient_list, self.fail_silently, self.html)
        mail_sent_queue.put(True)


def _send_mail(subject, body, from_email, recipient_list,
               fail_silently=False, html=None):
    msg = EmailMultiAlternatives(subject, body, from_email, recipient_list)
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send(fail_silently)


def send_mail(subject, body, from_email, recipient_list,
              fail_silently=False, html=None):
    if settings.COMMENTS_XTD_THREADED_EMAILS:
        EmailThread(subject, body, from_email, recipient_list,
                    fail_silently, html).start()
    else:
        _send_mail(subject, body, from_email, recipient_list,
                   fail_silently, html)


def import_formatter():
    try:
        from django_markup.markup import formatter
        # from markdown import markdown
        # from docutils import core
        return formatter
    except ImportError:
        return False
