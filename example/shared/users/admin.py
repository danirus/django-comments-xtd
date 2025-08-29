from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import Confirmation, User


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    # add_form_template = "admin/users/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "name",
                        "email",
                        "password",
                        "is_active",
                        "url",
                    )
                )
            },
        ),
        (
            "Date Information",
            {
                "fields": (("date_joined", "last_login"),),
                "classes": ("collapse"),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "name", "last_login", "is_active", "date_joined")
    list_display_links = ("email",)
    ordering = ("id",)
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("name", "email")
    date_hierarchy = "date_joined"
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


@admin.register(Confirmation)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_out_of_date",
        "purpose",
        "notifications",
        "key",
    )
    list_display_links = ("email",)
    date_hierarchy = "creation_date"
