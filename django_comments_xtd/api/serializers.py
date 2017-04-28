from django_comments_xtd.conf import settings
from django.utils.translation import ugettext as _

from django_comments import signals
from django_comments.models import CommentFlag
from rest_framework import serializers

from django_comments_xtd.models import XtdComment, LIKEDIT_FLAG, DISLIKEDIT_FLAG


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=50, read_only=True)
    user_email = serializers.CharField(max_length=254, read_only=True)
    user_url = serializers.CharField(read_only=True)
    submit_date = serializers.DateTimeField(read_only=True)
    thread_id = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(default=0)
    level = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    followup = serializers.BooleanField(write_only=True, default=False)
    is_removed = serializers.BooleanField(read_only=True)

    comment = serializers.SerializerMethodField()
    likedit_users = serializers.SerializerMethodField()
    dislikedit_users = serializers.SerializerMethodField()
    
    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_email', 'user_url', 'comment',
                  'submit_date', 'thread_id', 'parent_id', 'level', 'order',
                  'followup', 'is_removed', 'likedit_users', 'dislikedit_users'
        )

    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return obj.comment

    def get_likedit_users(self, obj):
        return [settings.COMMENTS_XTD_API_USER_REPR(user)
                for user in obj.users_who_liked_it()]

    def get_dislikedit_users(self, obj):
        return [settings.COMMENTS_XTD_API_USER_REPR(user)
                for user in obj.users_who_disliked_it()]


class FlagSerializer(serializers.ModelSerializer):
    flag_choices = {'like': LIKEDIT_FLAG, 'dislike': DISLIKEDIT_FLAG}

    class Meta:
        model = CommentFlag
        fields = ('comment', 'flag',)

    def validate_flag(self, value):
        if value not in self.flag_choices:
            raise serializers.ValidationError("Invalid flag.")
        return self.flag_choices[value]
