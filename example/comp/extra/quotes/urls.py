from django.urls import re_path
from django.views.generic import ListView

from comp.extra.quotes.models import Quote
from comp.extra.quotes.views import QuoteDetailView


urlpatterns = [
    re_path(r'^$', ListView.as_view(queryset=Quote.objects.published()),
            name='quotes-index'),

    re_path((r'^(?P<slug>[-\w]+)/$'), QuoteDetailView.as_view(),
            name='quotes-quote-detail'),
]
