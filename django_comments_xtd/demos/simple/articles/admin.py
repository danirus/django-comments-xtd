from django.contrib import admin

from simple.articles.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publish', 'allow_comments')
    list_filter   = ('publish',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None, 
                  {'fields': ('title', 'slug', 'body', 
                              'allow_comments', 'publish',)}),)

admin.site.register(Article, ArticleAdmin)
