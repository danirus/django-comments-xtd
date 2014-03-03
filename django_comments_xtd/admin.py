from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd import get_model as get_comment_model


XtdComment = get_comment_model()

class XtdCommentsAdmin(CommentsAdmin):
    list_display = ('thread_level', 'cid', 'name', 'content_type', 'object_pk', 'ip_address', 'submit_date', 'followup', 'is_public', 'is_removed')
    list_display_links = ('cid',)
    list_filter = ('content_type', 'is_public', 'is_removed', 'followup')
    fieldsets = (
        (None,          {'fields': ('content_type', 'object_pk', 'site')}),
        (_('Content'),  {'fields': ('user', 'user_name', 'user_email', 
                                    'user_url', 'comment', 'followup')}),
        (_('Metadata'), {'fields': ('submit_date', 'ip_address',
                                    'is_public', 'is_removed')}),
    )
    date_hierarchy = 'submit_date'
    ordering = ('thread_id', 'order')

    def thread_level(self, obj):
        rep = '|'
        if obj.level:
            rep += '-' * obj.level
            rep += " c%d to c%d" % (obj.id, obj.parent_id)
        else: 
            rep += " c%d" % obj.id
        return rep

    def cid(self, obj):
        return 'c%d' % obj.id

admin.site.register(XtdComment, XtdCommentsAdmin)
