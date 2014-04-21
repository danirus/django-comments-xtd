from django.conf.urls import patterns, include, url
from django.contrib import admin
from django_comments.feeds import LatestCommentFeed


admin.autodiscover()

urlpatterns = patterns('multiple.views',
    url(r'^admin/',           include(admin.site.urls)),
    url(r'^blog/',            include('multiple.blog.urls')),
    url(r'^projects/',        include('multiple.projects.urls')),
    url(r'^comments/',        include('django_comments_xtd.urls')),
    url(r'^$',                'homepage_v',        name='homepage'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),
)
