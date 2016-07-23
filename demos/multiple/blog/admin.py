from django.contrib import admin

from multiple.blog.models import Story, Quote


class StoryAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publish', 'allow_comments')
    list_filter   = ('publish',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None, 
                  {'fields': ('title', 'slug', 'body', 
                              'allow_comments', 'publish',)}),)

admin.site.register(Story, StoryAdmin)


class QuoteAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publish', 'allow_comments')
    list_filter   = ('publish',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None, 
                  {'fields': ('title', 'slug', 'quote', 'author', 'url_source',
                              'allow_comments', 'publish',)}),)

admin.site.register(Quote, QuoteAdmin)
