from django.urls import path
from django_cypress.views import (
    CreateUserView,
    CSRFTokenView,
    ManageView,
    MigrateView,
    RefreshDatabaseView,
)

urlpatterns = [
    path("manage/", ManageView.as_view(), name="manage-view"),
    path(
        "refreshDatabase/",
        RefreshDatabaseView.as_view(),
        name="refresh-database-view",
    ),
    path("migrate/", MigrateView.as_view(), name="migrate-view"),
    path("csrftoken/", CSRFTokenView.as_view(), name="csrftoken-view"),
    path("createUser/", CreateUserView.as_view(), name="create-user-view"),
]
