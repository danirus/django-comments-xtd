from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django_comments_xtd import LatestCommentFeed
from django_comments_xtd.views import XtdCommentListView

from comp import views

admin.autodiscover()


urlpatterns = [
    url(r'^$', views.HomepageView.as_view(), name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^articles/', include('comp.articles.urls')),
    url(r'^quotes/', include('comp.quotes.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^comments/$', XtdCommentListView.as_view(
        content_types=["articles.article", "quotes.quote"]),
        name='comments-xtd-list'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
