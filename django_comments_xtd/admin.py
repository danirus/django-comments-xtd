from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd.models import XtdComment

class XtdCommentsAdmin(CommentsAdmin):
    list_display = ('name', 'content_type', 'object_pk', 'ip_address', 'submit_date', 'followup', 'is_public', 'is_removed')
    fieldsets = (
        (None,          {'fields': ('content_type', 'object_pk', 'site')}),
        (_('Content'),  {'fields': ('user', 'user_name', 'user_email', 
                                    'user_url', 'comment', 'followup')}),
        (_('Metadata'), {'fields': ('submit_date', 'ip_address',
                                    'is_public', 'is_removed')}),
    )
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)

admin.site.register(XtdComment, XtdCommentsAdmin)
