from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from django_comments_xtd import LatestCommentFeed


admin.autodiscover()


urlpatterns = [                       
    url(r'^$',
        TemplateView.as_view(template_name="homepage.html"),
        name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^articles/', include('custom.articles.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^feeds/comments/$', LatestCommentFeed(), name='comments-feed'),    
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
