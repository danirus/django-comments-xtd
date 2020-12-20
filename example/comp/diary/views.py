from django.urls import reverse
from django.views.generic import DateDetailView
from django.views.generic.dates import _date_from_string

from .models import Diary


class DiaryDetailView(DateDetailView):
    model = Diary
    date_field = "publish"
    month_format = "%m"
    allow_future = False

    def get_object(self, queryset=None):
        return super().get_object(queryset=queryset)
