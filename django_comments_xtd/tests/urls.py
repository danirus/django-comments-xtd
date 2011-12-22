from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^articles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        'django_comments_xtd.tests.views.dummy_view',
        name='articles-article-detail'),

    (r'^comments/', include('django_comments_xtd.urls')),
)
