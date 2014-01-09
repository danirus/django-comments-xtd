from django.conf.urls import patterns, url
from django.views.generic import ListView, DateDetailView, DetailView

from multiple.projects import views

urlpatterns = patterns('',
    url(r'^$', 
        views.ProjectsView.as_view(), 
        name='projects-index'),

    url(r'^(?P<slug>[-\w]+)/$', 
        views.ProjectDetailView.as_view(),
        name='projects-project-detail'),

    url(r'^(?P<project_slug>[-\w]+)/(?P<release_slug>[-\w]+)/$', 
        views.ReleaseDetailView.as_view(),
        name='projects-release-detail'),
)

