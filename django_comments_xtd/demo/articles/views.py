from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import DateDetailView

from demo.articles.models import Article


class ArticleDetail(DateDetailView):
    model = Article
    date_field = "publish"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(DateDetailView, self).get_context_data(**kwargs)
        context['next'] = reverse("comments-xtd-confirmation-requested")
        return context    


