from django.urls import path

from tests.specs.views import AllSpecsView, LoggedOutSpecDetailView

urlpatterns = [
    path("", AllSpecsView.as_view(), name="all-specs"),
    path(
        "logged-out/<slug:slug>/",
        LoggedOutSpecDetailView.as_view(),
        name="logged-out-spec-detail",
    ),
]
