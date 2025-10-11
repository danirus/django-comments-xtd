from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django_comments.feeds import LatestCommentFeed
from rest_framework.schemas import get_schema_view

from comp import views
from django_comments_xtd.views import XtdCommentListView

try:
    from drf_spectacular.views import SpectacularAPIView
    has_drf_spectacular = True
except ImportError:
    has_drf_spectacular = False

admin.autodiscover()


urlpatterns = [
    re_path(r"^$", views.HomepageView.as_view(), name="homepage"),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
    re_path(r"^articles/", include("comp.articles.urls")),
    re_path(r"^quotes/", include("comp.extra.quotes.urls")),
    re_path(r"^comments/", include("django_comments_xtd.urls")),
    re_path(
        r"^comments/$",
        XtdCommentListView.as_view(
            content_types=["articles.article", "quotes.quote"],
            paginate_by=10,
            page_range=5,
        ),
        name="comp-comment-list",
    ),
    re_path(r"^feeds/comments/$", LatestCommentFeed(), name="comments-feed"),
    re_path(
        r"^api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    re_path(
        r"^jsi18n/$", JavaScriptCatalog.as_view(), name="javascript-catalog"
    ),
    re_path(r"admin/", admin.site.urls),
]

if has_drf_spectacular:
    urlpatterns.append(
        path('openapi', SpectacularAPIView.as_view(), name='openapi-schema'),
    )
else:
    urlpatterns.append(
        re_path(
            "openapi",
            get_schema_view(
                title="django-comments-xtd API",
                description="Example Comp Project - API",
                version="1.0.0",
            ),
            name="openapi-schema",
        )
    )


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *staticfiles_urlpatterns(),
    ]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]
