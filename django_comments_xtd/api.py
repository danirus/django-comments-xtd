from django.http import Http404

from rest_framework import generics

from django_comments_xtd.models import XtdComment
from django_comments_xtd.serializers import XtdCommentSerializer


class XtdCommentList(generics.ListCreateAPIView):
    """List all comments or create a new comment."""
    queryset = XtdComment.objects.all()
    serializer_class = XtdCommentSerializer


class XtdCommentDetail(generics.RetrieveUpdateAPIView):
    """Retrieve or update a comment instance."""
    queryset = XtdComment.objects.all()
    serializer_class = XtdCommentSerializer
