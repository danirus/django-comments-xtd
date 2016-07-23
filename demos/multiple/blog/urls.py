import django
if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns, url
else:
    from django.conf.urls import url

from django.views.generic import ListView, DateDetailView, DetailView

from django_comments_xtd.models import XtdComment

from multiple.blog.models import Story, Quote
from multiple.blog.views import (homepage, StoryDetailView, QuoteDetailView,
                                 CommentsView)


pattern_list = [
    url(r'^$', homepage, name='blog-index'),

    url(r'^stories$', 
        ListView.as_view(queryset=Story.objects.published()),
        name='blog-story-index'),

    url(r'^quotes$', 
        ListView.as_view(queryset=Quote.objects.published()),
        name='blog-quote-index'),

    url(r'^story/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        StoryDetailView.as_view(),
        name='blog-story-detail'),

    url(r'^quote/(?P<slug>[-\w]+)/$', 
        QuoteDetailView.as_view(),
        name='blog-quote-detail'),

    # list all comments using pagination, newer first
    url(r'^comments$',
        CommentsView.as_view(),
        name='blog-comments'),
]

urlpatterns = None

if django.VERSION[:2] < (1, 8):
    urlpatterns = patterns('', *pattern_list)
else:
    urlpatterns = pattern_list
