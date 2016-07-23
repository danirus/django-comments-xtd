from django.core.urlresolvers import reverse
from django.views.generic import DateDetailView

from django_comments.signals import comment_will_be_posted

from example.articles.models import Article


class ArticleDetailView(DateDetailView):
    model = Article
    date_field = "publish"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context


# Replace this by subclassing CommentModerator (in a class defined inside
# django-comments-xtd that will search in a list of black listed spamming
# domains. The list of black listed domains is provided by
# http://www.joewein.de/sw/bl-text.htm).
# def discard_comments_from_badly(sender, comment, request, **kwargs):
#     """Discard comments when email address for verification ends with bad.ly."""
#     if comment.get('comment', ''):
#         return False
# comment_will_be_posted.connect(discard_comments_from_badly)

# Also define another CommentModerator subclass that can be use to put a hold
# on comments that contain rude or hate speech.

# See http://django-contrib-comments.readthedocs.org/en/latest/moderation.html
# to implement both subclasses.
