from django.conf.urls import patterns, include, url
from django.contrib import admin
from django_comments.feeds import LatestCommentFeed


admin.autodiscover()

urlpatterns = patterns('views',
    url(r'^admin/',           include(admin.site.urls)),
    url(r'^articles/',        include('simple_threads.articles.urls')),
    url(r'^comments/',        include('django_comments_xtd.urls')),
    url(r'^$',                'homepage_v',        name='homepage'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
)
