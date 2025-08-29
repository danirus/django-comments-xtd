from django.contrib import admin

from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_time", "allow_comments")
    list_filter = ("published_time",)
    search_fields = ("title", "quote", "author")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "quote",
                    "author",
                    "url_source",
                    "allow_comments",
                    "published_time",
                )
            },
        ),
    )


admin.site.register(Quote, QuoteAdmin)
