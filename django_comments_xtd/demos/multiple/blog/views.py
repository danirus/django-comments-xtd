from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import DateDetailView, DetailView, ListView

from django_comments_xtd.models import XtdComment

from multiple.blog.models import Story, Quote


def homepage(request):
    stories = Story.objects.published()[:1]
    quotes = Quote.objects.published()[:5]
    return render_to_response("blog/homepage.html",
                              { "stories": stories, "quotes": quotes },
                              context_instance=RequestContext(request))


class StoryDetailView(DateDetailView):
    model = Story
    date_field = "publish"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context
        

class QuoteDetailView(DetailView):
    model = Quote
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context


class CommentsView(ListView):
    template_name = "django_comments_xtd/blog/comment_list.html"
    paginate_by = 5

    def get_queryset(self):
        return XtdComment.objects.for_app_models("blog.story", "blog.quote")
