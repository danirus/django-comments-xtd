from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django_comments.feeds import LatestCommentFeed
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns('simple.views',
    url(r'^admin/',           include(admin.site.urls)),
    url(r'^articles/',        include('simple.articles.urls')),
    url(r'^comments/',        include('django_comments_xtd.urls')),
    url(r'^$',                'homepage_v',        name='homepage'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
