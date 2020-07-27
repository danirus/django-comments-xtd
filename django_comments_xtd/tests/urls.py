from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path

from django_comments_xtd.tests import views

urlpatterns = [
    re_path(r'^accounts/login/$', auth_views.LoginView),
    re_path(r'^articles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
            r'(?P<slug>[-\w]+)/$',
            views.dummy_view,
            name='article-detail'),
    re_path(r'^diary/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/',
            views.dummy_view,
            name='diary-detail'),
    re_path(r'^comments/', include('django_comments_xtd.urls')),

    re_path(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
]
urlpatterns += staticfiles_urlpatterns()
