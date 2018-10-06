import django
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

if django.VERSION[:2] < (2, 0):
    from django.conf.urls import include, url as re_path
else:
    from django.urls import include, re_path

from django_comments_xtd import LatestCommentFeed

from custom import views


admin.autodiscover()


urlpatterns = [                       
    re_path(r'^$', views.HomepageView.as_view(), name='homepage'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^articles/', include('custom.articles.urls')),
    re_path(r'^comments/', include('django_comments_xtd.urls')),
    re_path(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
