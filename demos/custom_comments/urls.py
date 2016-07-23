import django
if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns, include, url
else:
    from django.conf.urls import include, url
    
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django_comments_xtd import LatestCommentFeed

from custom_comments import views

admin.autodiscover()

pattern_list = [                       
    url(r'^admin/', include(admin.site.urls)),
    url(r'^articles/', include('custom_comments.articles.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^$', views.homepage_v, name='homepage'),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
]

urlpatterns = None

if django.VERSION[:2] < (1, 8):
    urlpatterns = patterns('custom_comments.views', *patterns_list)
else:
    urlpatterns = pattern_list

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
