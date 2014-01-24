from django.conf.urls import patterns, url
from django.views.generic import ListView, DateDetailView, DetailView

from django_comments_xtd.models import XtdComment

from multiple.blog.models import Story, Quote
from multiple.blog.views import homepage, StoryDetailView, QuoteDetailView

urlpatterns = patterns('',
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
        ListView.as_view(
            queryset=XtdComment.objects.for_app_models("blog.story", 
                                                       "blog.quote"), 
            template_name="django_comments_xtd/blog/comment_list.html",
            paginate_by=5),
        name='blog-comments'),
)
