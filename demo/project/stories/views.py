from django.urls import reverse
from django.views.generic import DateDetailView

from .models import Story


class StoryDetailView(DateDetailView):
    model = Story
    date_field = "published_time"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context
