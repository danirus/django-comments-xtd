from django.conf.urls.defaults import patterns, include, url

from django_comments_xtd import views

urlpatterns = patterns('',
    url(r'', include("django.contrib.comments.urls")),

    url(r'^confirm/(?P<key>[^/]+)$', 
        views.confirm,
        name='comments-xtd-confirm'),

    url(r'^confirmation-requested$', 
        views.confirmation_requested, 
        name="comments-xtd-confirmation-requested")
)

