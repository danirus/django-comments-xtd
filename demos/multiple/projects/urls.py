import django
if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns, url
else:
    from django.conf.urls import url

from django.views.generic import ListView, DateDetailView, DetailView

from multiple.projects import views


pattern_list = [
    url(r'^$', 
        views.ProjectsView.as_view(), 
        name='projects-index'),

    url(r'^(?P<slug>[-\w]+)/$', 
        views.ProjectDetailView.as_view(),
        name='projects-project-detail'),

    url(r'^(?P<project_slug>[-\w]+)/(?P<release_slug>[-\w]+)/$', 
        views.ReleaseDetailView.as_view(),
        name='projects-release-detail'),
]

urlpatterns = None

if django.VERSION[:2] < (1, 8):
    urlpatterns = patterns('', *pattern_list)
else:
    urlpatterns = pattern_list


