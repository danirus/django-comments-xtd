from django.contrib import admin

from .models import Story


@admin.register(Story)
class ArticleAdmin(admin.ModelAdmin):
    list_display  = ('title', 'published_time', 'allow_comments')
    list_filter   = ('published_time',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None,
                  {'fields': ('title', 'slug', 'body',
                              'allow_comments', 'published_time',)}),)
