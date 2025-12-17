from django.http import HttpResponse

from django_comments_xtd.api import views


def dummy_view(request, *args, **kwargs):
    return HttpResponse("Got it")


class AltCommentReactionAuthorsList(views.CommentReactionAuthorsList):
    pagination_class = None
