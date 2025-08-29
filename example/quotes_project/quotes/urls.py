from django.urls import path

from .views import QuoteDetailView, QuoteListView

urlpatterns = [
    path("", QuoteListView.as_view(), name="quotes"),
    path("<slug:slug>/", QuoteDetailView.as_view(), name="quote-detail"),
]
