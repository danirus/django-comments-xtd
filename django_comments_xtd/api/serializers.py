import hashlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
    
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from django_comments import signals
from django_comments.models import CommentFlag
from rest_framework import serializers

from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment, LIKEDIT_FLAG, DISLIKEDIT_FLAG
from django_comments_xtd.templatetags.comments_xtd import render_markup_comment
from django_comments_xtd.utils import get_app_model_permissions


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=50, read_only=True)
    user_email = serializers.CharField(max_length=254, write_only=True)
    user_url = serializers.CharField(read_only=True)
    user_moderator = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    submit_date = serializers.DateTimeField(read_only=True,
                                            format="%B %-d, %Y, %-I:%M %p")
    thread_id = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(default=0)
    level = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    followup = serializers.BooleanField(write_only=True, default=False)
    is_removed = serializers.BooleanField(read_only=True)
    comment = serializers.SerializerMethodField()
    allow_reply = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    flags = serializers.SerializerMethodField()
    
    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_email', 'user_url', 'user_moderator',
                  'user_avatar', 'permalink', 'comment', 'submit_date',
                  'thread_id', 'parent_id', 'level', 'order', 'followup',
                  'is_removed', 'allow_reply', 'flags'
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs['context']['request']
        super(CommentSerializer, self).__init__(*args, **kwargs)
        
    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return render_markup_comment(obj.comment)

    def get_user_moderator(self, obj):
        try:
            if obj.user and obj.user.has_perm('comments.can_moderate'):
                return True
            else:
                return False
        except:
            return None

    def get_flags(self, obj):
        flags = {
            'like': {'active': False, 'users': None},
            'dislike': {'active': False, 'users': None},
            'removal': {'active': False, 'count': None},
        }
        users_likedit, users_dislikedit = None, None
        
        if get_app_model_permissions(obj)['allow_flagging']:
            users_flagging = obj.users_flagging(CommentFlag.SUGGEST_REMOVAL)
            if self.request.user in users_flagging:
                flags['removal']['active'] = True
            if self.request.user.has_perm("django_comments.can_moderate"):
                flags['removal']['count'] = len(users_flagging)
 
        if (
                get_app_model_permissions(obj)['allow_feedback'] or
                get_app_model_permissions(obj)['show_feedback']
        ):
            users_likedit = obj.users_flagging(LIKEDIT_FLAG)
            users_dislikedit = obj.users_flagging(DISLIKEDIT_FLAG)
            
        if get_app_model_permissions(obj)['allow_feedback']:
            if self.request.user in users_likedit:
                flags['like']['active'] = True
            elif self.request.user in users_dislikedit:
                flags['dislike']['active'] = True
        if get_app_model_permissions(obj)['show_feedback']:
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
        # Check commenting permissions on object being commented.
        permission = ''
        if data['flag'] in ['like', 'dislike']:
            permission = 'allow_feedback'
        elif data['flag'] == 'report':
            permission = 'allow_flagging'
        comment = data['comment']
        if not get_app_model_permissions(comment)[permission]:
            ctype = ContentType.objects.get_for_model(comment.content_object)
            raise serializers.ValidationError(
                "Comments posted to instances of '%s.%s' are not explicitly "
                "allowed to receive '%s' flags. Check "
                "COMMENTS_XTD_APP_MODEL_PERMISSIONS setting." % (
                    ctype.app_label, ctype.model, data['flag']
                )
            )
        data['flag'] = self.flag_choices[data['flag']]
        return data
