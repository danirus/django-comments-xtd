from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views import generic

from django_comments_xtd import views, models


COMMENTS_XTD_LIST_URL_ACTIVE = getattr(settings, 
                                       'COMMENTS_XTD_LIST_URL_ACTIVE', False)
COMMENTS_XTD_LIST_PAGINATE_BY = getattr(settings, 
                                        'COMMENTS_XTD_LIST_PAGINATE_BY', 10)

urlpatterns = patterns('',
    url(r'', include("django.contrib.comments.urls")),

    url(r'^confirm/(?P<key>[^/]+)$', 
        views.confirm,
        name='comments-xtd-confirm'),

    url(r'^confirmation-requested$', 
        views.confirmation_requested, 
        name="comments-xtd-confirmation-requested")
)

if COMMENTS_XTD_LIST_URL_ACTIVE:
    urlpatterns += patterns('',
        url(r'^list$', 
            generic.ListView.as_view(model=models.XtdComment, 
                                     paginate_by=COMMENTS_XTD_LIST_PAGINATE_BY),
            name='comments-list'),
    )
