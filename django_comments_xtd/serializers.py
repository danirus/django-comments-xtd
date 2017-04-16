from rest_framework import serializers
from django_comments_xtd.models import XtdComment


class XtdCommentSerializer(serializers.ModelSerializer):
    submit_date = serializers.DateTimeField(read_only=True)
    thread_id = serializers.IntegerField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    followup = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = XtdComment
        fields = ('id', 'user_name', 'user_email', 'user_url', 'comment',
                  'submit_date', 'thread_id', 'parent_id', 'level',
                  'order', 'followup')
