from django.conf.urls import url
from django.views.generic import ListView

from .models import Story
from .views import StoryDetailView


urlpatterns = [
    url(r'^$',
        ListView.as_view(queryset=Story.objects.published()),
        name='stories'),

    url((r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
         r'(?P<slug>[-\w]+)/$'),
        StoryDetailView.as_view(),
        name='story-detail'),

]