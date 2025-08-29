from django.urls import path, re_path

from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),
    re_path(
        r"^register/(?P<key>[^/]+)/confirm$",
        views.user_register_confirm,
        name="register-confirm",
    ),
    path("reset-password/", views.user_reset_password, name="reset-password"),
    re_path(
        r"^reset-password/(?P<key>[^/]+)/confirm$",
        views.user_reset_password_confirm,
        name="reset-password-confirm",
    ),
    path("account/", views.user_account, name="account"),
    path("account/edit/", views.edit_profile, name="edit-profile"),
    re_path(
        r"^account/change-email/(?P<key>[^/]+)/confirm$",
        views.confirm_change_email,
        name="change-email-confirm",
    ),
    path("account/password/", views.edit_password, name="edit-password"),
    path("account/cancel/", views.user_delete, name="delete"),
    re_path(
        r"^account/cancel/(?P<key>[^/]+)/confirm$",
        views.user_delete_confirm,
        name="delete-confirm",
    ),
]
