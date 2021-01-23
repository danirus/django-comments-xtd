from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils import formats, timezone
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _, activate, get_language

from django_comments import get_form
from django_comments.forms import CommentSecurityForm
from django_comments.models import CommentFlag
from django_comments.signals import comment_will_be_posted, comment_was_posted
from rest_framework import exceptions, serializers

from django_comments_xtd import get_model, signed, views
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (TmpXtdComment, XtdComment,
                                        LIKEDIT_FLAG, DISLIKEDIT_FLAG,
                                        max_thread_level_for_content_type)
from django_comments_xtd.signals import (should_request_be_authorized,
                                         confirmation_received)
from django_comments_xtd.utils import get_app_model_options


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class WriteCommentSerializer(serializers.Serializer):
    content_type = serializers.CharField()
    object_pk = serializers.CharField()
    timestamp = serializers.CharField(required=False)
    security_hash = serializers.CharField(required=False)
    honeypot = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    url = serializers.URLField(required=False)
    comment = serializers.CharField(max_length=COMMENT_MAX_LENGTH)
    followup = serializers.BooleanField(default=False)
    reply_to = serializers.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        self.request = kwargs['context']['request']
        super(WriteCommentSerializer, self).__init__(*args, **kwargs)

    def validate_name(self, value):
        if not len(value):
            if (
                not len(self.request.user.get_full_name())
                or not self.request.user.is_authenticated
            ):
                raise serializers.ValidationError("This field is required")
            else:
                return (self.request.user.get_full_name() or
                        self.request.user.get_username())
        return value

    def validate_email(self, value):
        if not len(value):
            if (
                not len(self.request.user.email) or
                not self.request.user.is_authenticated
            ):
                raise serializers.ValidationError("This field is required")
            else:
                return self.request.user.email
        return value

    def validate_reply_to(self, value):
        if value != 0:
            try:
                parent = get_model().objects.get(pk=value)
            except get_model().DoesNotExist:
                raise serializers.ValidationError(
                    "reply_to comment does not exist")
            else:
                max = max_thread_level_for_content_type(parent.content_type)
                if parent.level == max:
                    raise serializers.ValidationError(
                        "Max thread level reached")
        return value

    def validate(self, data):
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        if ctype is None or object_pk is None:
            return serializers.ValidationError("Missing content_type or "
                                               "object_pk field.")
        try:
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.get(pk=object_pk)
            whocan = get_app_model_options(content_type=ctype)['who_can_post']
        except (AttributeError, TypeError, LookupError):
            raise serializers.ValidationError("Invalid content_type value: %r"
                                              % escape(ctype))
        except model.ObjectDoesNotExist:
            raise serializers.ValidationError(
                "No object matching content-type %r and object PK %r exists."
                % (escape(ctype), escape(object_pk)))
        except (ValueError, serializers.ValidationError) as e:
            raise serializers.ValidationError(
                "Attempting to get content-type %r and object PK %r exists "
                "raised %s" % (escape(ctype), escape(object_pk),
                               e.__class__.__name__))
        else:
            if whocan == "users" and not self.request.user.is_authenticated:
                raise serializers.ValidationError("User not authenticated")

        # Signal that the request allows to be authorized.
        responses = should_request_be_authorized.send(
            sender=target.__class__,
            comment=target,
            request=self.request
        )

        for (receiver, response) in responses:
            if response is True:
                # A positive response indicates that the POST request
                # must be trusted. So inject the CommentSecurityForm values
                # to pass the form validation step.
                secform = CommentSecurityForm(target)
                data.update({
                    "honeypot": "",
                    "timestamp": secform['timestamp'].value(),
                    "security_hash": secform['security_hash'].value()
                })
                break
        self.form = get_form()(target, data=data)

        # Check security information.
        if self.form.security_errors():
            raise exceptions.PermissionDenied()
        if self.form.errors:
            raise serializers.ValidationError(self.form.errors)
        return data

    def save(self):
        # resp object is a dictionary. The code key indicates the possible
        # four states the comment can be in:
        #  * Comment created (http 201),
        #  * Confirmation sent by mail (http 204),
        #  * Comment in moderation (http 202),
        #  * Comment rejected (http 403),
        #  * Comment have bad data (http 400).
        site = get_current_site(self.request)
        resp = {
            'code': -1,
            'comment': self.form.get_comment_object(site_id=site.id)
        }
        resp['comment'].ip_address = self.request.META.get("REMOTE_ADDR", None)

        if self.request.user.is_authenticated:
            resp['comment'].user = self.request.user

        # Signal that the comment is about to be saved
        responses = comment_will_be_posted.send(sender=TmpXtdComment,
                                                comment=resp['comment'],
                                                request=self.request)
        for (receiver, response) in responses:
            if response is False:
                resp['code'] = 403  # Rejected.
                return resp

        # Replicate logic from django_comments_xtd.views.on_comment_was_posted.
        if (
            not settings.COMMENTS_XTD_CONFIRM_EMAIL or
            self.request.user.is_authenticated
        ):
            if views._get_comment_if_exists(resp['comment']) is None:
                new_comment = views._create_comment(resp['comment'])
                resp['comment'].xtd_comment = new_comment
                confirmation_received.send(sender=TmpXtdComment,
                                           comment=resp['comment'],
                                           request=self.request)
                comment_was_posted.send(sender=new_comment.__class__,
                                        comment=new_comment,
                                        request=self.request)
                if resp['comment'].is_public:
                    resp['code'] = 201
                    views.notify_comment_followers(new_comment)
                else:
                    resp['code'] = 202
        else:
            key = signed.dumps(resp['comment'], compress=True,
                               extra_key=settings.COMMENTS_XTD_SALT)
            views.send_email_confirmation_request(resp['comment'], key, site)
            resp['code'] = 204  # Confirmation sent by mail.

        return resp


class FlagSerializer(serializers.ModelSerializer):
    flag_choices = {'like': LIKEDIT_FLAG,
                    'dislike': DISLIKEDIT_FLAG,
                    'report': CommentFlag.SUGGEST_REMOVAL}

    class Meta:
        model = CommentFlag
        fields = ('comment', 'flag',)

    def validate(self, data):
        # Validate flag.
        if data['flag'] not in self.flag_choices:
            raise serializers.ValidationError("Invalid flag.")
        # Check commenting options on object being commented.
        option = ''
        if data['flag'] in ['like', 'dislike']:
            option = 'allow_feedback'
        elif data['flag'] == 'report':
            option = 'allow_flagging'
        comment = data['comment']
        ctype = ContentType.objects.get_for_model(comment.content_object)
        key = "%s.%s" % (ctype.app_label, ctype.model)
        if not get_app_model_options(content_type=key)[option]:
            raise serializers.ValidationError(
                "Comments posted to instances of '%s' are not explicitly "
                "allowed to receive '%s' flags. Check the "
                "COMMENTS_XTD_APP_MODEL_OPTIONS setting." % (key, data['flag'])
            )
        data['flag'] = self.flag_choices[data['flag']]
        return data


class ReadFlagField(serializers.RelatedField):
    def to_representation(self, value):
        if value.flag == CommentFlag.SUGGEST_REMOVAL:
            flag = "removal"
        elif value.flag == LIKEDIT_FLAG:
            flag = "like"
        elif value.flag == DISLIKEDIT_FLAG:
            flag = "dislike"
        else:
            raise Exception('Unexpected value for flag: %s' % value.flag)
        return {
            "flag": flag,
            "user": settings.COMMENTS_XTD_API_USER_REPR(value.user),
            "id": value.user.id
        }


class ReadCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=50, read_only=True)
    user_url = serializers.CharField(read_only=True)
    user_moderator = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    submit_date = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(default=0, read_only=True)
    level = serializers.IntegerField(read_only=True)
    is_removed = serializers.BooleanField(read_only=True)
    comment = serializers.SerializerMethodField()
    allow_reply = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    flags = ReadFlagField(many=True, read_only=True)

    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_url', 'user_moderator',
                  'user_avatar', 'permalink', 'comment', 'submit_date',
                  'parent_id', 'level', 'is_removed', 'allow_reply', 'flags')

    def __init__(self, *args, **kwargs):
        self.request = kwargs['context']['request']
        super(ReadCommentSerializer, self).__init__(*args, **kwargs)

    def get_submit_date(self, obj):
        activate(get_language())
        if settings.USE_TZ:
            submit_date = timezone.localtime(obj.submit_date)
        else:
            submit_date = obj.submit_date
        return formats.date_format(submit_date, 'DATETIME_FORMAT',
                                   use_l10n=True)

    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return obj.comment

    def get_user_moderator(self, obj):
        try:
            if obj.user and obj.user.has_perm('django_comments.can_moderate'):
                return True
            else:
                return False
        except Exception:
            return None

    def get_allow_reply(self, obj):
        return obj.allow_thread()

    def get_user_avatar(self, obj):
        return import_string(settings.COMMENTS_XTD_API_GET_USER_AVATAR)(obj)

    def get_permalink(self, obj):
        return obj.get_absolute_url()
