from django.contrib.auth import logout
from django.urls import reverse
from django.views.generic import DetailView, TemplateView

from tests.specs.models import LoggedOutSpec


class AllSpecsView(TemplateView):
    template_name = "homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["logged_out_specs"] = LoggedOutSpec.objects.all()
        return context


class LoggedOutSpecDetailView(DetailView):
    model = LoggedOutSpec

    def get_context_data(self, **kwargs):
        logout(self.request)
        context = super().get_context_data(**kwargs)
        context.update({"next": reverse("comments-xtd-sent")})
        return context
