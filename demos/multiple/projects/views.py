from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import DetailView, ListView

from multiple.projects.models import Project, Release


class ProjectsView(ListView):
    queryset = Project.objects.filter(is_active=True)
    template_name = "projects/homepage.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectsView, self).get_context_data(**kwargs)

        items = []
        for project in self.object_list:
            try:
                last_published_release = project.release_set.filter(
                    is_active=True).order_by("-release_date")[0]
            except IndexError:
                continue
            else:
                items.append({"project": project, 
                              "release": last_published_release})

        if len(items):
            items.sort(key=lambda item: item['release'].release_date, 
                       reverse=True)

        context['items'] = items
        return context


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['release_list'] = []
        for release in self.get_object().release_set.filter(is_active=True).order_by("-release_date"):
            context['release_list'].append(release)
        return context


class ReleaseDetailView(DetailView):
    model = Release

    def get_object(self, queryset=None):
        project_pk = self.kwargs.get('project_slug', None)
        release_slug = self.kwargs.get('release_slug', None)
        try:
            obj = Release.objects.get(project=project_pk, slug=release_slug)
        except ObjectDoesNotExist:
            raise Http404(_("No releases found matching the query"))
        return obj

    def get_context_data(self, **kwargs):
        context = super(ReleaseDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context
        
