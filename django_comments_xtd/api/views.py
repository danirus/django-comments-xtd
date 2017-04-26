from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from rest_framework import generics, permissions

from django_comments_xtd.models import XtdComment
from django_comments_xtd.api.permissions import IsOwnerOrReadOnly
from django_comments_xtd.api.serializers import XtdCommentSerializer


class XtdCommentList(generics.ListCreateAPIView):
    """List all comments or create a new comment."""

    serializer_class = XtdCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        qs = XtdComment.objects.filter(content_type=content_type,
                                       object_pk=int(object_pk_arg),
                                       is_public=True)
        return qs

    def perform_create(self, serializer):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        kwargs = {
            'content_type': content_type,
            'object_pk': int(object_pk_arg),
            'site_id': settings.SITE_ID,
            'user': self.request.user,
            'user_name': (self.request.user.get_full_name() or
                          self.request.user.get_username()),
            'user_email': self.request.user.email,
            'ip_address': self.request.META.get('REMOTE_ADDR', None)
        }
        serializer.save(**kwargs)


class XtdCommentDetail(generics.RetrieveUpdateAPIView):
    """Retrieve or update a comment instance."""

    queryset = XtdComment.objects.all()
    serializer_class = XtdCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
