import hashlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

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
    submit_date = serializers.DateTimeField(read_only=True,
                                            format="%B %-d, %Y, %-I:%M %p")
    thread_id = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(default=0)
    level = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    followup = serializers.BooleanField(write_only=True, default=False)
    is_removed = serializers.BooleanField(read_only=True)

    comment = serializers.SerializerMethodField()
    ilikedit = serializers.SerializerMethodField()
    idislikedit = serializers.SerializerMethodField()
    likedit_users = serializers.SerializerMethodField()
    dislikedit_users = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    reply_url = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_email', 'user_url', 'is_moderator',
                  'avatar', 'permalink', 'comment', 'submit_date', 'thread_id',
                  'parent_id', 'level', 'order', 'followup', 'is_removed',
                  'reply_url', 'likedit_users', 'dislikedit_users',
                  'ilikedit', 'idislikedit', 
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs['context']['request']
        super(CommentSerializer, self).__init__(*args, **kwargs)
        
    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return render_markup_comment(obj.comment)

    def get_is_moderator(self, obj):
        try:
            if obj.user and obj.user.has_perm('comments.can_moderate'):
                return True
            else:
                return False
        except:
            return None
        
    def get_ilikedit(self, obj):
        try:
            if self.request.user in obj.users_who_liked_it():
                return True
            else:
                return False
        except:
            return None

    def get_idislikedit(self, obj):
        try:
            if self.request.user in obj.users_who_disliked_it():
                return True
            else:
                return False
        except:
            return None
            
    def get_likedit_users(self, obj):
        if get_app_model_permissions(obj)['show_feedback']:
            return [settings.COMMENTS_XTD_API_USER_REPR(user)
                    for user in obj.users_who_liked_it()]
        else:
            return None

    def get_dislikedit_users(self, obj):
        if get_app_model_permissions(obj)['show_feedback']:
            return [settings.COMMENTS_XTD_API_USER_REPR(user)
                    for user in obj.users_who_disliked_it()]
        else:
            return None

    def get_reply_url(self, obj):
        if obj.allow_thread():
            return obj.get_reply_url()
        else:
            return None
        
    def get_avatar(self, obj):
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
