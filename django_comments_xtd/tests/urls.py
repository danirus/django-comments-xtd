from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django_comments_xtd.tests import views

urlpatterns = [
    url(r'^accounts/login/$', auth_views.LoginView),
    url(r'^articles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
        r'(?P<slug>[-\w]+)/$',
        views.dummy_view,
        name='article-detail'),
    url(r'^diary/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/',
        views.dummy_view,
        name='diary-detail'),
    url(r'^comments/', include('django_comments_xtd.urls')),
]
urlpatterns += staticfiles_urlpatterns()
