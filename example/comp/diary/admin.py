from django.contrib import admin

from .models import Diary


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display  = ('truncated_body', 'publish', 'allow_comments')
    list_filter   = ('publish',)
    search_fields = ('body',)

    def truncated_body(self, obj):
        return "%s" % obj
