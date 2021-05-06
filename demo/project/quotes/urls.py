from django.conf.urls import url

from .views import QuoteDetailView, QuoteListView


urlpatterns = [
    url(r'^$', QuoteListView.as_view(), name='quotes'),

    url((r'^(?P<slug>[-\w]+)/$'), QuoteDetailView.as_view(),
        name='quote-detail'),
]
