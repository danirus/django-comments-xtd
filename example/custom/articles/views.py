from django.urls import reverse
from django.views.generic import DateDetailView

from articles.models import Article


class ArticleDetailView(DateDetailView):
    model = Article
    date_field = "publish"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context
