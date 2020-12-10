import six

from django.db.models import F, Prefetch
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string

from django_comments.models import CommentFlag
from django_comments_xtd import get_model as get_comment_model
from django_comments.views.moderation import perform_flag
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from django_comments_xtd import views
from django_comments_xtd.conf import settings
from django_comments_xtd.api import serializers
from django_comments_xtd.models import (TmpXtdComment, XtdComment,
                                        CommentReaction)
from django_comments_xtd.utils import (get_app_model_options,
                                       get_current_site_id)


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
        app, model = content_type_arg.split("-")
        try:
            content_type = ContentType.objects.get_by_natural_key(app, model)
        except ContentType.DoesNotExist:
            qs = XtdComment.objects.none()
        else:
            return XtdComment.get_queryset(content_type=content_type,
                                           object_pk=object_pk_arg)


class CommentCount(generics.GenericAPIView):
    """Get number of comments posted to a given ContentType and object ID."""
    serializer_class = serializers.ReadCommentSerializer

    def get_queryset(self):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        site_id = getattr(settings, "SITE_ID", None)
        if not site_id:
            site_id = get_current_site_id(self.request)
        fkwds = {
            "content_type": content_type,
            "object_pk": object_pk_arg,
            "site__pk": site_id,
            "is_public": True
        }
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True):
            fkwds["is_removed"] = False
        return get_comment_model().objects.filter(**fkwds)

    def get(self, request, *args, **kwargs):
        return Response({'count': self.get_queryset().count()})


def check_allow_feedback_option(comment):
    is_allowed = get_app_model_options(comment=comment)['allow_feedback']
    if not is_allowed:
        message = "This comment does not accept reactions."
        if settings.DEBUG:
            ct = ContentType.objects.get_for_model(comment.content_object)
            message = ("Comments posted to instances of '%s.%s' are not "
                       "explicitly allowed to receive reactions. "
                       "Check the COMMENTS_XTD_APP_MODEL_OPTIONS "
                       "setting." % (ct.app_label, ct.model))
        raise PermissionDenied(detail=message,
                               code=status.HTTP_403_FORBIDDEN)


class CreateReportFlag(generics.CreateAPIView):
    """Create 'removal suggestion' flags."""

    serializer_class = serializers.FlagSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(get_comment_model(),
                                    pk=int(request.data['comment']))
        check_allow_feedback_option(comment)
        return super(CreateReportFlag, self).post(request, *args, **kwargs)

    def perform_create(self, serializer):
        perform_flag(self.request, serializer.validated_data['comment'])


@api_view(["POST"])
def preview_user_avatar(request):
    """Fetch the image associated with the user previewing the comment."""
    temp_comment = TmpXtdComment({
        'user': None,
        'user_email': request.data['email']
    })
    if request.user.is_authenticated:
        temp_comment['user'] = request.user
    get_user_avatar = import_string(settings.COMMENTS_XTD_API_GET_USER_AVATAR)
    return Response({'url': get_user_avatar(temp_comment)})


class PostCommentReaction(mixins.CreateModelMixin,
                          generics.GenericAPIView):
    """Create and delete comment reactions."""

    serializer_class = serializers.WriteCommentReactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(get_comment_model(),
                                    pk=int(request.data['comment']))
        check_allow_feedback_option(comment)
        self.create(request, *args, **kwargs)
        # Create a new response object with the list of reactions the
        # comment has received. If other users sent reactions they all will
        # be reflected in the comment, not only the reaction sent with this
        # particular request.
        if self.created:
            return Response(comment.get_reactions(),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(comment.get_reactions(),
                            status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        cr_qs = CommentReaction.objects.filter(
            authors=self.request.user, **serializer.validated_data)
        if cr_qs.count() == 1:  # It does already exist, do nothing.
            self.created = False
            cr_qs.update(counter=F('counter') - 1)
            cr_qs[0].authors.remove(self.request.user)
        else:
            creaction, _ = CommentReaction.objects.get_or_create(
                **serializer.validated_data)
            creaction.authors.add(self.request.user)
            # self.created is True when the user reacting is added.
            self.created = True
            creaction.counter += 1
            creaction.save()
