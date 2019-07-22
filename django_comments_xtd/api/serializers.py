import hashlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils import formats
from django.utils.html import escape
from django.utils.translation import ugettext as _, activate, get_language

from django_comments import get_form
from django_comments.models import CommentFlag
from django_comments.signals import comment_will_be_posted, comment_was_posted
from rest_framework import serializers

from django_comments_xtd import signed, views
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (TmpXtdComment, XtdComment,
                                        LIKEDIT_FLAG, DISLIKEDIT_FLAG)
from django_comments_xtd.signals import confirmation_received
from django_comments_xtd.utils import has_app_model_option


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class WriteCommentSerializer(serializers.Serializer):
    content_type = serializers.CharField()
    object_pk = serializers.CharField()
    timestamp = serializers.CharField()
    security_hash = serializers.CharField()
    honeypot = serializers.CharField(allow_blank=True)
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

    def validate(self, data):
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        if ctype is None or object_pk is None:
            return serializers.ValidationError("Missing content_type or "
                                               "object_pk field.")
        try:
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.get(pk=object_pk)
        except TypeError:
            return serializers.ValidationError("Invalid content_type value: %r"
                                               % escape(ctype))
        except AttributeError:
            return serializers.ValidationError("The given content-type %r does "
                                               "not resolve to a valid model."
                                               % escape(ctype))
        except model.ObjectDoesNotExist:
            return serializers.ValidationError(
                "No object matching content-type %r and object PK %r exists."
                % (escape(ctype), escape(object_pk)))
        except (ValueError, serializers.ValidationError) as e:
            return serializers.ValidationError(
                "Attempting go get content-type %r and object PK %r exists "
                "raised %s" % (escape(ctype), escape(object_pk),
                               e.__class__.__name__))

        self.form = get_form()(target, data=data)

        # Check security information
        if self.form.security_errors():
            return serializers.ValidationError(
                "The comment form failed security verification: %s" %
                escape(str(self.form.security_errors())))
        if self.form.errors:
            return serializers.ValidationError(self.form.errors)
        return data

    def save(self):
        # resp object is a dictionary. The code key indicates the possible
        # four states the comment can be in:
        #  * Comment created (http 201),
        #  * Confirmation sent by mail (http 204),
        #  * Comment in moderation (http 202),
        #  * Comment rejected (http 403).
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
            if not views._comment_exists(resp['comment']):
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
    flags = serializers.SerializerMethodField()

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
        return formats.date_format(obj.submit_date, 'DATETIME_FORMAT',
                                   use_l10n=True)

    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return obj.comment

    def get_user_moderator(self, obj):
        try:
            if obj.user and obj.user.has_perm('comments.can_moderate'):
                return True
            else:
                return False
        except Exception:
            return None

    def get_flags(self, obj):
        flags = {
            'like': {'active': False, 'users': None},
            'dislike': {'active': False, 'users': None},
            'removal': {'active': False, 'count': None},
        }
        users_likedit, users_dislikedit = None, None

        if has_app_model_option(obj)['allow_flagging']:
            users_flagging = obj.users_flagging(CommentFlag.SUGGEST_REMOVAL)
            if self.request.user in users_flagging:
                flags['removal']['active'] = True
            if self.request.user.has_perm("django_comments.can_moderate"):
                flags['removal']['count'] = len(users_flagging)

        if (
                has_app_model_option(obj)['allow_feedback'] or
                has_app_model_option(obj)['show_feedback']
        ):
            users_likedit = obj.users_flagging(LIKEDIT_FLAG)
            users_dislikedit = obj.users_flagging(DISLIKEDIT_FLAG)

        if has_app_model_option(obj)['allow_feedback']:
            if self.request.user in users_likedit:
                flags['like']['active'] = True
            elif self.request.user in users_dislikedit:
                flags['dislike']['active'] = True
        if has_app_model_option(obj)['show_feedback']:
            flags['like']['users'] = [
                "%d:%s" % (user.id, settings.COMMENTS_XTD_API_USER_REPR(user))
                for user in users_likedit]
            flags['dislike']['users'] = [
                "%d:%s" % (user.id, settings.COMMENTS_XTD_API_USER_REPR(user))
                for user in users_dislikedit]
        return flags

    def get_allow_reply(self, obj):
        return obj.allow_thread()

    def get_user_avatar(self, obj):
        path = hashlib.md5(obj.user_email.lower().encode('utf-8')).hexdigest()
        param = urlencode({'s': 48})
        return "http://www.gravatar.com/avatar/%s?%s&d=mm" % (path, param)

    def get_permalink(self, obj):
        return obj.get_absolute_url()


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
        if not has_app_model_option(comment)[option]:
            ctype = ContentType.objects.get_for_model(comment.content_object)
            raise serializers.ValidationError(
                "Comments posted to instances of '%s.%s' are not explicitly "
                "allowed to receive '%s' flags. Check the "
                "COMMENTS_XTD_APP_MODEL_OPTIONS setting." % (
                    ctype.app_label, ctype.model, data['flag']
                )
            )
        data['flag'] = self.flag_choices[data['flag']]
        return data
