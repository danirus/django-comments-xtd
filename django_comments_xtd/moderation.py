from django import VERSION
from django.conf import settings
try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site

from django.template import Context, loader

try:
    from django_comments import get_model
    from django_comments.signals import (comment_will_be_posted,
                                         comment_was_flagged)
    from django_comments.models import CommentFlag
    from django_comments.moderation import Moderator, CommentModerator
except ImportError:
    from django.contrib.comments import get_model
    from django.contrib.comments.signals import (comment_will_be_posted,
                                                 comment_was_flagged)
    from django.contrib.comments.models import CommentFlag
    from django.contrib.comments.moderation import Moderator, CommentModerator

from django_comments_xtd.models import BlackListedDomain, TmpXtdComment
from django_comments_xtd.signals import confirmation_received
from django_comments_xtd.utils import send_mail


class XtdCommentModerator(CommentModerator):
    """
    Encapsulates comment-moderation options for a given-model.

    This class extends ``django_comments.moderation.CommentModerator``. It's not
    designed to be used directly, since it doesn't enable any of the available
    moderation options. Instead, subclass it and override attributes to enable
    different options::

    ``removal_suggestion_notification``
        If ``True``, any new removal suggestion flag on an object
        of this model will generate an email to site staff. Default
        value is ``False``.

    Check parent class to see inherited options.

    Most common moderation needs can be covered by changing option attributes,
    but further customization can be obtained by subclassing and overriding
    the following method::

    ``notify_removal_suggestion``
         If removal suggestion notifications should be sent to site staff
         or moderators, this method is responsible for sending the email.

    Check the parent class to read about methods ``allow``, ``email``, and
    ``moderate``.

    """
    removal_suggestion_notification = None

    def notify_removal_suggestion(self, comment, content_object, request):
        if not self.removal_suggestion_notification:
            return
        recipient_list = [manager_tuple[1]
                          for manager_tuple in settings.MANAGERS]
        t = loader.get_template('django_comments_xtd/'
                                'removal_notification_email.txt')
        c = {'comment': comment,
             'content_object': content_object,
             'current_site': get_current_site(request),
             'request': request}
        subject = ('[%s] Comment removal suggestion on "%s"' %
                   (c['current_site'].name, content_object))
        message = t.render(Context(c) if VERSION < (1, 8) else c)
        send_mail(subject, message, settings.COMMENTS_XTD_FROM_EMAIL,
                  recipient_list, fail_silently=True)


class SpamModerator(XtdCommentModerator):
    """
    Discard messages comming from blacklisted domains.

    The current list of blacklisted domains had been fetched from
    http://www.joewein.net/spam/blacklist.htm

    You can download for free a recent version of the list, and subscribe
    to get notified on changes. Changes can be fetched with rsync for a
    small fee (check their conditions, or use any other Spam filter).

    django-comments-xtd approach against spam consist of requiring comment
    confirmation by email. However spam comments could be discarded even
    before sending the confirmation email by searching sender's domain in
    the list of blacklisted domains.

    ``SpamModerator`` uses the additional ``django_comments_xtd`` model:
     * ``BlackListedDomain``

    Remember to update the content regularly through an external Spam
    filtering service.
    """
    def allow(self, comment, content_object, request):
        try:
            domain = comment.user_email.split('@', 1)[1]
        except IndexError:
            return False
        else:
            if(BlackListedDomain.objects.filter(domain=domain).count()):
                return False
            return super(SpamModerator, self).allow(comment, content_object,
                                                    request)


class XtdModerator(Moderator):
    def connect(self):
        comment_will_be_posted.connect(self.pre_save_moderation,
                                       sender=TmpXtdComment)
        confirmation_received.connect(self.post_save_moderation,
                                      sender=TmpXtdComment)
        comment_was_flagged.connect(self.comment_flagged,
                                    sender=get_model())

    def comment_flagged(self, sender, comment, flag, created, request,
                        **kwargs):
        model = comment.content_type.model_class()
        if model not in self._registry:
            return
        if flag.flag is not CommentFlag.SUGGEST_REMOVAL:
            return
        self._registry[model].notify_removal_suggestion(comment,
                                                        comment.content_object,
                                                        request)

moderator = XtdModerator()
