import django
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from django_comments_xtd import LatestCommentFeed

from simple import views


admin.autodiscover()


urlpatterns = [
    re_path(r'^$', views.HomepageView.as_view(), name='homepage'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^articles/', include('simple.articles.urls')),
    re_path(r'^comments/', include('django_comments_xtd.urls')),
    re_path(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + staticfiles_urlpatterns()
