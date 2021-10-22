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


def comments_api_props(obj, user, request=None):
    """
    Returns a JSON object with the initial props for the CommentBox component.

    The returned JSON object contains the following attributes::
        {
            comment_count: <int>,  // Count of comments posted to the object.
            input_allowed: <bool>,  // Whether to allow comments to this post.
            current_user: <str as "user_id:user_name">,
            is_authenticated: <bool>,  // Whether current_user is authenticated.
            request_name: <bool>,  // True when auth user has no actual name.
            request_email_address: <bool>,  // True when auth user has no email.
            is_authenticated: <bool>,
            who_can_post: 'users' | 'all',
            comment_flagging_enabled: <bool>,
            comment_reactions_enabled: <bool>,
            object_reactions_enabled: <bool>,
            can_moderate: <bool>,  // Whether current_user can moderate.
            react_url: <api-url-to-send-reactions-to-comments>,
            delete_url: <api-url-for-moderators-to-remove-comment>,
            reply_url: <api-url-to-reply-comments>,
            flag_url: <api-url-to-suggest-comment-removal>,
            list_url: <api-url-to-list-comments>,
            count_url: <api-url-to-count-comments>,
            send_url: <api-url-to-send-a-comment>,
            form: {
                content_type: <value>,
                object_pk: <value>,
                timestamp: <value>,
                security_hash: <value>
            },
            login_url: <only_when_user_is_not_authenticated>,
            html_id_suffix: <html_element_id_suffix>,
            max_thread_level: max_thread_level for the content type of the obj.
        }
    """
    form = CommentSecurityForm(obj)
    ctype = ContentType.objects.get_for_model(obj)
    queryset = XtdComment.objects.filter(content_type=ctype,
                                         object_pk=obj.pk,
                                         site__pk=get_current_site_id(request),
                                         is_public=True)
    ctype_slug = "%s-%s" % (ctype.app_label, ctype.model)
    app_model = "%s.%s" % (ctype.app_label, ctype.model)
    options = get_app_model_options(content_type=app_model)
    check_input_allowed_str = options.pop('check_input_allowed')
    check_func = import_string(check_input_allowed_str)
    d = {
        "comment_count": queryset.count(),
        "input_allowed": check_func(obj),
        "current_user": "0:Anonymous",
        "request_name": False,
        "request_email_address": False,
        "is_authenticated": False,
        "who_can_post": options['who_can_post'],
        "comment_flagging_enabled": options['comment_flagging_enabled'],
        "comment_reactions_enabled": options['comment_reactions_enabled'],
        "object_reactions_enabled": options['object_reactions_enabled'],
        "can_moderate": False,
        "react_url": reverse("comments-xtd-api-react"),
        "delete_url": reverse("comments-delete", args=(0,)),
        "reply_url": reverse("comments-xtd-reply", kwargs={'cid': 0}),
        "flag_url": reverse("comments-xtd-api-flag"),
        "list_url": reverse('comments-xtd-api-list',
                            kwargs={'content_type': ctype_slug,
                                    'object_pk': obj.id}),
        "count_url": reverse('comments-xtd-api-count',
                             kwargs={'content_type': ctype_slug,
                                     'object_pk': obj.id}),
        "send_url": reverse("comments-xtd-api-create"),
        "form": {
            "content_type": form['content_type'].value(),
            "object_pk": form['object_pk'].value(),
            "timestamp": form['timestamp'].value(),
            "security_hash": form['security_hash'].value()
        },
        "default_followup": settings.COMMENTS_XTD_DEFAULT_FOLLOWUP,
        "html_id_suffix": get_html_id_suffix(obj),
        "max_thread_level": max_thread_level_for_content_type(ctype),
    }
    if user and user.is_authenticated:
        d['current_user'] = "%d:%s" % (
            user.pk, settings.COMMENTS_XTD_API_USER_REPR(user))
        d['is_authenticated'] = True
        d['can_moderate'] = user.has_perm("django_comments.can_moderate")
        d['request_name'] = True if not len(user.get_full_name()) else False
        d['request_email_address'] = True if not user.email else False
    else:
        d['login_url'] = settings.LOGIN_URL

    return d


def comments_api_props_response(obj, user, request):
    """Return a Response containing React props for use with client-side JS.
    Can add as an extra action to a ViewSet as follows:

        @action(detail=True, methods=['get'],
                permission_classes=[permissions.IsAuthenticated])
        def comments_api_props(self, request, *args, **kwargs):
            return comments_api_props_response(self.get_object(),
                                               request.user, request)
    """
    return Response(data=comments_api_props(obj, user, request=request))
