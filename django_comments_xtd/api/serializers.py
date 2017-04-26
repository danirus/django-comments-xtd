from django.utils.translation import ugettext as _

from django_comments import signals
from rest_framework import serializers

from django_comments_xtd.models import XtdComment


class XtdCommentSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField()
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
    
    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_email', 'user_url', 'comment',
                  'submit_date', 'thread_id', 'parent_id', 'level',
                  'order', 'followup', 'is_removed')

    def get_comment(self, obj):
        if obj.is_removed:
            return _("This comment has been removed.")
        else:
            return obj.comment
