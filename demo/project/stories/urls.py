from django.conf.urls import url

from .views import StoryDetailView, StoryListView


urlpatterns = [
    url(r'^$', StoryListView.as_view(), name='stories'),

    url((r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
         r'(?P<slug>[-\w]+)/$'),
        StoryDetailView.as_view(),
        name='story-detail'),

]