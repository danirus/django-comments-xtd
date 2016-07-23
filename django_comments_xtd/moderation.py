try:
    from django_comments.signals import comment_will_be_posted
    from django_comments.moderation import Moderator, CommentModerator
except ImportError:
    from django.contrib.comments.signals import comment_will_be_posted
    from django.contrib.comments.moderation import Moderator, CommentModerator

from django_comments_xtd.models import BlackListedDomain, TmpXtdComment
from django_comments_xtd.signals import confirmation_received


class SpamModerator(CommentModerator):
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
        # comment_was_posted.connect(self.post_save_moderation,
        #                            sender=TmpXtdComment)
        confirmation_received.connect(self.post_save_moderation,
                                      sender=TmpXtdComment)

moderator = XtdModerator()
