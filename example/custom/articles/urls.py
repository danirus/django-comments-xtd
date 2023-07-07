from django.urls import re_path
from django.views.generic import ListView

from articles.models import Article
from articles.views import ArticleDetailView


urlpatterns = [
    re_path(
        r'^$',
        ListView.as_view(queryset=Article.objects.published()),
        name='articles-index'),

    re_path(
        (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
         r'(?P<slug>[-\w]+)/$'),
        ArticleDetailView.as_view(),
        name='articles-article-detail'),
]
