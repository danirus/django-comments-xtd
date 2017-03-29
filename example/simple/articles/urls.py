from django.conf.urls import url    
from django.views.generic import ListView, DateDetailView

from simple.articles.models import Article
from simple.articles.views import ArticleDetailView


urlpatterns = [
    url(r'^$', 
        ListView.as_view(queryset=Article.objects.published()),
        name='articles-index'),

    url((r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
         r'(?P<slug>[-\w]+)/$'),
        ArticleDetailView.as_view(), 
        name='articles-article-detail'),
]
