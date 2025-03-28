import django
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if django.VERSION[:2] < (2, 0):
    from django.conf.urls import include
    from django.conf.urls import url as re_path
else:
    from django.urls import include, path, re_path

import views
from django_comments.feeds import LatestCommentFeed

admin.autodiscover()


urlpatterns = [
    re_path(r"^$", views.HomepageView.as_view(), name="homepage"),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^articles/", include("articles.urls")),
    re_path(r"^comments/", include("django_comments_xtd.urls")),
    re_path(r"^feeds/comments/$", LatestCommentFeed(), name="comments-feed"),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *staticfiles_urlpatterns(),
    ]
