from articles.models import Article
from django.urls import reverse
from django.views.generic import DateDetailView


class ArticleDetailView(DateDetailView):
    model = Article
    date_field = "publish"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"next": reverse("comments-xtd-sent")})
        return context
