from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from django_comments.models import CommentFlag
from django_comments.views.moderation import perform_flag
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django_comments_xtd import views
from django_comments_xtd.api import serializers
from django_comments_xtd.models import XtdComment


class CommentCreate(generics.CreateAPIView):
    """Create a comment."""
    serializer_class = serializers.WriteCommentSerializer

    def post(self, request, *args, **kwargs):
        response = super(CommentCreate, self).post(request, *args, **kwargs)
        if self.comment.user and self.comment.user.is_authenticated():
            # The comment has been created without need for further
            # confirmation, however it could be held for approval, or
            # be immediately discarded.
            return response
        else:
            return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        self.comment = serializer.save()


class CommentList(generics.ListCreateAPIView):
    """List all comments for a given ContentType and object ID."""

    serializer_class = serializers.ReadCommentSerializer
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


class ToggleFeedbackFlag(generics.CreateAPIView, mixins.DestroyModelMixin):
    """Create and delete like/dislike flags."""

    serializer_class = serializers.FlagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        response = super(ToggleFeedbackFlag, self).post(request, *args,
                                                        **kwargs)
        if self.created:
            return response
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        f = getattr(views, 'perform_%s' % self.request.data['flag'])
        self.created = f(self.request, serializer.validated_data['comment'])


class CreateReportFlag(generics.CreateAPIView):
    """Create 'removal suggestion' flags."""

    serializer_class = serializers.FlagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        return super(CreateReportFlag, self).post(request, *args, **kwargs)

    def perform_create(self, serializer):
        perform_flag(self.request, serializer.validated_data['comment'])
