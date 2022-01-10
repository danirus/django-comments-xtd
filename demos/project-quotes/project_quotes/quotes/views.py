from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Quote, check_comments_input_allowed


class QuoteListView(ListView):
    def get_queryset(self):
        return Quote.objects.published()


class QuoteDetailView(DetailView):
    model = Quote

    def get_context_data(self, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(**kwargs)
        obj = context.get('object')
        context.update({
            'next': reverse('comments-xtd-sent'),
            'is_comment_input_allowed': check_comments_input_allowed(obj)
        })
        return context
