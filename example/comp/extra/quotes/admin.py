from django.contrib import admin

from comp.extra.quotes.models import Quote

class QuoteAdmin(admin.ModelAdmin):
    list_display  = ('title', 'author', 'publish', 'allow_comments')
    list_filter   = ('publish',)
    search_fields = ('title', 'quote', 'author')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None, 
                  {'fields': ('title', 'slug', 'quote', 'author', 'url_source',
                              'allow_comments', 'publish',)}),)

admin.site.register(Quote, QuoteAdmin)
