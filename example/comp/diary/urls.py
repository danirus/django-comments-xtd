from django.conf.urls import url
from django.views.generic import ListView
from django.views.generic.dates import DayArchiveView

from .models import Diary
from .views import DiaryDetailView


urlpatterns = [
    url(r'^$',
        ListView.as_view(queryset=Diary.objects.published(),
                         paginate_by=10),
        name='diary-index'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/',
        DayArchiveView.as_view(queryset=Diary.objects.published(),
                               date_field="publish",
                               ordering="publish"),
        name='diary-day'),
]
