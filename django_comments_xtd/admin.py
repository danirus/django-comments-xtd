# ruff:noqa: RUF012
from django.contrib import admin
from django_comments import get_model
from django_comments.admin import CommentsAdmin
from django_comments.models import CommentFlag

from django_comments_xtd.models import BlackListedDomain, XtdComment


class XtdCommentsAdmin(CommentsAdmin):
    list_display = (
        "cid",
        "thread_level",
        "nested_count",
        "name",
        "content_type",
        "object_pk",
        "ip_address",
        "submit_date",
        "followup",
        "is_public",
        "is_removed",
    )
    list_display_links = ("cid",)
    list_filter = ("content_type", "is_public", "is_removed", "followup")
    fieldsets = (
        (None, {"fields": ("content_type", "object_pk", "site")}),
        (
            "Content",
            {
                "fields": (
                    "user",
                    "user_name",
                    "user_email",
                    "user_url",
                    "comment",
                    "followup",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "submit_date",
                    "ip_address",
                    "is_public",
                    "is_removed",
                )
            },
        ),
    )
    date_hierarchy = "submit_date"
    ordering = ("thread_id", "order")
    search_fields = [
        "object_pk",
        "user__username",
        "user_name",
        "user_email",
        "comment",
    ]

    def thread_level(self, obj):
        rep = "|"
        if obj.level:
            rep += "-" * obj.level
            rep += f" c{obj.id} to c{obj.parent_id}"
        else:
            rep += f" c{obj.id}"
        return rep

    def cid(self, obj):
        return f"c{obj.id}"


class BlackListedDomainAdmin(admin.ModelAdmin):
    search_fields = ["domain"]


if get_model() is XtdComment:
    admin.site.register(XtdComment, XtdCommentsAdmin)
    admin.site.register(CommentFlag)
    admin.site.register(BlackListedDomain, BlackListedDomainAdmin)
