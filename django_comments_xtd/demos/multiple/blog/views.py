from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import DateDetailView

from multiple.blog.models import Story, Quote


def homepage(request):
    stories = Story.objects.published()[:1]
    quotes = Quote.objects.published()[:5]
    return render_to_response("blog/homepage.html",
                              { "stories": stories, "quotes": quotes },
                              context_instance=RequestContext(request))
