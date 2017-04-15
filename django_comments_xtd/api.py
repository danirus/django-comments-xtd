from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from rest_framework import generics

from django_comments_xtd.models import XtdComment
from django_comments_xtd.serializers import XtdCommentSerializer


class XtdCommentList(generics.ListCreateAPIView):
    """List all comments or create a new comment."""
    serializer_class = XtdCommentSerializer

    def get_queryset(self):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        qs = XtdComment.objects.filter(content_type=content_type,
                                       object_pk=int(object_pk_arg),
                                       is_public=True,
                                       is_removed=False)
        return qs

    def perform_create(self, serializer):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        serializer.save(content_type=content_type, object_pk=int(object_pk_arg))
        

class XtdCommentDetail(generics.RetrieveUpdateAPIView):
    """Retrieve or update a comment instance."""
    queryset = XtdComment.objects.all()
    serializer_class = XtdCommentSerializer
