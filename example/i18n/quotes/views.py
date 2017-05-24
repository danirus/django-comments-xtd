from django.core.urlresolvers import reverse
from django.views.generic import DetailView

from i18n.quotes.models import Quote


class QuoteDetailView(DetailView):
    model = Quote

    def get_context_data(self, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context
