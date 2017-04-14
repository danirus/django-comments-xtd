from rest_framework import serializers
from django_comments_xtd.models import XtdComment


class XtdCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = XtdComment
        fields = ('id', 'content_type', 'object_pk', 'site', 'user',
                  'user_name', 'user_email', 'user_url', 'comment',
                  'submit_date', 'is_public', 'is_removed', 'thread_id',
                  'parent_id', 'level', 'order', 'followup')
        
