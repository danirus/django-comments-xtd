from django.conf.urls import url
from django.views.generic import ListView, DateDetailView

from i18n.quotes.models import Quote
from i18n.quotes.views import QuoteDetailView


urlpatterns = [
    url(r'^$', ListView.as_view(queryset=Quote.objects.published()),
        name='quotes-index'),

    url((r'^(?P<slug>[-\w]+)/$'), QuoteDetailView.as_view(), 
        name='quotes-quote-detail'),
]
