from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView

admin.autodiscover()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("shared.users.urls")),
    path("specs/", include("tests.specs.urls")),
    path("comments/", include("django_comments_xtd.urls")),
    path("", RedirectView.as_view(pattern_name="all-specs"), name="homepage"),
    *staticfiles_urlpatterns(),
]
