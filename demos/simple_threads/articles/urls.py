import django
if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns, url
else:
    from django.conf.urls import url

from django.views.generic import ListView, DateDetailView

from simple_threads.articles.models import Article
from simple_threads.articles.views import ArticleDetailView


pattern_list = [
    url(r'^$', 
        ListView.as_view(queryset=Article.objects.published()),
        name='articles-index'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        ArticleDetailView.as_view(), 
        name='articles-article-detail'),
]

urlpatterns = None
if django.VERSION[:2] < (1, 8):
    urlpatterns = patterns('', *pattern_list)
else:
    urlpatterns = pattern_list

