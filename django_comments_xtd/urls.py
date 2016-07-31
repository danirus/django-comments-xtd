import django
from django_comments_xtd import views
from django_comments_xtd.conf import settings

if django.VERSION[:2] < (1, 4):
    from django.conf.urls.defaults import include, patterns, url
else:
    if django.VERSION[:2] < (1, 8):
        from django.conf.urls import include, patterns, url
    else:
        from django.conf.urls import include, url

try:
    import django_comments.urls as django_comments_urls
except ImportError:
    import django.contrib.comments.urls as django_comments_urls


pattern_list = [
    url(r'', include(django_comments_urls)),
    url(r'^sent/$', views.sent, name='comments-xtd-sent'),
    url(r'^confirm/(?P<key>[^/]+)$', views.confirm,
        name='comments-xtd-confirm'),
    url(r'^mute/(?P<key>[^/]+)$', views.mute, name='comments-xtd-mute'),

    # New flags in addition to those provided by django-contrib-comments.
    url(r'^like/(\d+)/$', views.like, name='comments-xtd-like'),
    url(r'^liked/$', views.like_done, name='comments-xtd-like-done'),
    url(r'^dislike/(\d+)/$', views.dislike, name='comments-xtd-dislike'),
    url(r'^disliked/$', views.dislike_done, name='comments-xtd-dislike-done'),
]

urlpatterns = None

if django.VERSION[:2] < (1, 8):
    urlpatterns = patterns('', *pattern_list)
    if settings.COMMENTS_XTD_MAX_THREAD_LEVEL > 0:
        urlpatterns += patterns(
            "",
            url(r'^reply/(?P<cid>[\d]+)$', views.reply,
                name='comments-xtd-reply'),
        )
else:
    urlpatterns = pattern_list
    if settings.COMMENTS_XTD_MAX_THREAD_LEVEL > 0:
        urlpatterns.append(
            url(r'^reply/(?P<cid>[\d]+)$', views.reply,
                name='comments-xtd-reply')
        )
