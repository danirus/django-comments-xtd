from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DateDetailView

from demo.articles.models import Article
from demo.articles.views import ArticleDetail

urlpatterns = patterns('',
    url(r'^$', 
        ListView.as_view(queryset=Article.objects.published()),
        name='articles-index'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        ArticleDetail.as_view(), 
        name='articles-article-detail'),
)
