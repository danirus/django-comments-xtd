from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from django_comments.forms import CommentSecurityForm
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django_comments_xtd import get_model as get_comment_model
from django_comments_xtd.conf import settings
from django_comments_xtd.models import max_thread_level_for_content_type
from django_comments_xtd.utils import (
    get_current_site_id, get_app_model_options, get_html_id_suffix
)


XtdComment = get_comment_model()


class CommentBoxDriver(object):
    """
    Class that allows overriding methods like get_queryset()
    for CommentBox props function.
    """
    @classmethod
    def get_queryset(cls, ctype, obj, request):
        return XtdComment.objects.filter(
            content_type=ctype,
            object_pk=obj.pk,
            site__pk=get_current_site_id(request),
            is_public=True,
        )

    @classmethod
    def _reverse(cls, *args, **kwargs):
        """
        do not inject request to avoid http:// urls on https:// only sites
        """
        return reverse(*args, **kwargs)

    @classmethod
    def get_props(cls, obj, user, request=None):
        """
        Returns a JSON object with the initial props for
        the CommentBox component.

        The returned JSON object contains the following attributes::
            {
                comment_count: <int>,  // Count of comments posted
                                       // to the object.
                allow_comments: <bool>,  // Whether to allow comments
                                         // to this post.
                current_user: <str as "user_id:user_name">,
                is_authenticated: <bool>,  // Whether current_user
                                           // is authenticated.
                request_name: <bool>,  // True when auth user has
                                       // no actual name.
                request_email_address: <bool>,  // True when auth user
                                                // has no email.
                allow_flagging: false,
                allow_feedback: false,
                show_feedback: false,
                can_moderate: <bool>,  // Whether current_user can moderate.
                polling_interval: 2000, // Check for new comments
                                        // every 2 seconds.
                feedback_url: <api-url-to-send-like/dislike-feedback>,
                delete_url: <api-url-for-moderators-to-remove-comment>,
                login_url: settings.LOGIN_URL,
                reply_url: <api-url-to-reply-comments>,
                flag_url: <api-url-to-suggest-comment-removal>,
                list_url: <api-url-to-list-comments>,
                count_url: <api-url-to-count-comments>,
                send_url: <api-url-to-send-a-comment>,
                preview_url: <api-url-to-preview-users-avatar>,
                default_form: {
                    content_type: <value>,
                    object_pk: <value>,
                    timestamp: <value>,
                    security_hash: <value>
                },
                login_url: <only_when_user_is_not_authenticated>,
                like_url: <only_when_user_is_not_authenticated>,
                dislike_url: <only_when_user_is_not_authenticated>,
                html_id_suffix: <html_element_id_suffix>
            }
        """

        default_form = CommentSecurityForm(obj)
        ctype = ContentType.objects.get_for_model(obj)
        queryset = cls.get_queryset(ctype, obj, request)
        ctype_slug = "%s-%s" % (ctype.app_label, ctype.model)
        ctype_key = "%s.%s" % (ctype.app_label, ctype.model)
        options = get_app_model_options(content_type=ctype_key)
        d = {
            "comment_count": queryset.count(),
            "allow_comments": True,
            "current_user": "0:Anonymous",
            "request_name": False,
            "request_email_address": False,
            "is_authenticated": False,
            "who_can_post": options['who_can_post'],
            "allow_flagging": False,
            "allow_feedback": False,
            "show_feedback": False,
            "can_moderate": False,
            "polling_interval": 2000,
            "feedback_url": cls._reverse("comments-xtd-api-feedback"),
            "delete_url": cls._reverse("comments-delete", args=(0,)),
            "reply_url": cls._reverse("comments-xtd-reply", kwargs={'cid': 0}),
            "flag_url": cls._reverse("comments-flag", args=(0,)),
            "list_url": cls._reverse('comments-xtd-api-list',
                                     kwargs={'content_type': ctype_slug,
                                             'object_pk': obj.pk}),
            "count_url": cls._reverse('comments-xtd-api-count',
                                      kwargs={'content_type': ctype_slug,
                                              'object_pk': obj.pk}),
            "send_url": cls._reverse("comments-xtd-api-create"),
            "preview_url": cls._reverse("comments-xtd-api-preview"),
            "default_form": {
                "content_type": default_form['content_type'].value(),
                "object_pk": default_form['object_pk'].value(),
                "timestamp": default_form['timestamp'].value(),
                "security_hash": default_form['security_hash'].value()
            },
            "default_followup": settings.COMMENTS_XTD_DEFAULT_FOLLOWUP,
            "html_id_suffix": get_html_id_suffix(obj),
            "max_thread_level": max_thread_level_for_content_type(ctype),
            "comment_max_length": settings.COMMENT_MAX_LENGTH,
        }
        try:
            user_is_authenticated = user.is_authenticated()
        except TypeError:  # Django >= 1.11
            user_is_authenticated = user.is_authenticated
        if user and user_is_authenticated:
            d['current_user'] = "%d:%s" % (
                user.pk, settings.COMMENTS_XTD_API_USER_REPR(user))
            d['is_authenticated'] = True
            d['can_moderate'] = user.has_perm("django_comments.can_moderate")
            d['request_name'] = (
                True if not len(user.get_full_name()) else False
            )
            d['request_email_address'] = True if not user.email else False
        else:
            d['login_url'] = settings.LOGIN_URL
            d['like_url'] = reverse("comments-xtd-like", args=(0,))
            d['dislike_url'] = reverse("comments-xtd-dislike", args=(0,))

        return d


def commentbox_props(obj, user, request=None):
    """
    Returns a JSON object with the initial props for the CommentBox component.

    This is transitional function left for backward compatibility
    with applications that are using commentbox_props() function directly.
    """
    commentbox_class = import_string(settings.COMMENTS_XTD_COMMENTBOX_CLASS)
    return commentbox_class.get_props(obj, user, request)


def commentbox_props_response(obj, user, request):
    """Return a Response containing React props for use with client-side JS.
    Can add as an extra action to a ViewSet as follows:

        @action(detail=True, methods=['get'],
                permission_classes=[permissions.IsAuthenticated])
        def comment_props(self, request, *args, **kwargs):
            return commentbox_props_response(self.get_object(),
                                             request.user, request)
    """
    return Response(data=commentbox_props(obj, user, request=request))
