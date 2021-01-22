import six

from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from django_comments.models import CommentFlag
from django_comments.views.moderation import perform_flag
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django_comments_xtd import views
from django_comments_xtd.conf import settings
from django_comments_xtd.api import serializers
from django_comments_xtd.models import (
    TmpXtdComment, XtdComment, LIKEDIT_FLAG, DISLIKEDIT_FLAG
)
from django_comments_xtd.utils import get_current_site_id


class CommentCreate(generics.CreateAPIView):
    """Create a comment."""
    serializer_class = serializers.WriteCommentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response = super(CommentCreate, self).post(request, *args, **kwargs)
        else:
            if 'non_field_errors' in serializer.errors:
                response_msg = serializer.errors['non_field_errors'][0]
            else:
                response_msg = [k for k in six.iterkeys(serializer.errors)]
            return Response(response_msg, status=400)
        if self.resp_dict['code'] == 201:  # The comment has been created.
            response.data.update({
                'id': self.resp_dict['comment']['xtd_comment'].id
            })
            return response
        elif self.resp_dict['code'] in [202, 204, 403]:
            return Response({}, status=self.resp_dict['code'])

    def perform_create(self, serializer):
        self.resp_dict = serializer.save()


class CommentList(generics.ListAPIView):
    """List all comments for a given ContentType and object ID."""
    serializer_class = serializers.ReadCommentSerializer

    def get_queryset(self, **kwargs):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        try:
            content_type = ContentType.objects.get_by_natural_key(app_label,
                                                                  model)
        except ContentType.DoesNotExist:
            qs = XtdComment.objects.none()
        else:
            flags_qs = CommentFlag.objects.filter(flag__in=[
                CommentFlag.SUGGEST_REMOVAL, LIKEDIT_FLAG, DISLIKEDIT_FLAG
            ]).prefetch_related('user')
            prefetch = Prefetch('flags', queryset=flags_qs)
            qs = XtdComment\
                .objects\
                .prefetch_related(prefetch)\
                .filter(
                    content_type=content_type,
                    object_pk=object_pk_arg,
                    site__pk=get_current_site_id(self.request),
                    is_public=True
                )
        return qs


class CommentCount(generics.GenericAPIView):
    """Get number of comments posted to a given ContentType and object ID."""
    serializer_class = serializers.ReadCommentSerializer

    def get_queryset(self):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        qs = XtdComment.objects.filter(content_type=content_type,
                                       object_pk=object_pk_arg,
                                       is_public=True)
        return qs

    def get(self, request, *args, **kwargs):
        return Response({'count': self.get_queryset().count()})


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


@api_view(["POST"])
def preview_user_avatar(request):
    """Fetch the image associated with the user previewing the comment."""
    print("I am here")
    temp_comment = TmpXtdComment({
        'user': None,
        'user_email': request.data['email']
    })
    if request.user.is_authenticated:
        temp_comment['user'] = request.user
    get_user_avatar = import_string(settings.COMMENTS_XTD_API_GET_USER_AVATAR)
    return Response({'url': get_user_avatar(temp_comment)})
