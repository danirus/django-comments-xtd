from typing import ClassVar

from django.contrib import admin

from .models import (
    ArticleCommentsL0,
    ArticleCommentsL1,
    ArticleCommentsL2,
    ArticleCommentsL3,
    StoryCommentsL0,
    StoryCommentsL1,
    StoryCommentsL2,
    StoryCommentsL3,
    TaleCommentsL0,
    TaleCommentsL1,
    TaleCommentsL2,
    TaleCommentsL3,
)


class ProseCommonAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "published_time")
    list_filter = ("published_time",)
    search_fields = ("title", "body", "author")
    prepopulated_fields: ClassVar = {"slug": ("title",)}
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "body",
                    "allow_comments",
                    "published_time",
                )
            },
        ),
    )


admin.site.register(ArticleCommentsL0, ProseCommonAdmin)
admin.site.register(ArticleCommentsL1, ProseCommonAdmin)
admin.site.register(ArticleCommentsL2, ProseCommonAdmin)
admin.site.register(ArticleCommentsL3, ProseCommonAdmin)
admin.site.register(StoryCommentsL0, ProseCommonAdmin)
admin.site.register(StoryCommentsL1, ProseCommonAdmin)
admin.site.register(StoryCommentsL2, ProseCommonAdmin)
admin.site.register(StoryCommentsL3, ProseCommonAdmin)
admin.site.register(TaleCommentsL0, ProseCommonAdmin)
admin.site.register(TaleCommentsL1, ProseCommonAdmin)
admin.site.register(TaleCommentsL2, ProseCommonAdmin)
admin.site.register(TaleCommentsL3, ProseCommonAdmin)
