from django.views.generic import TemplateView


class HomepageView(TemplateView):
    template_name = "homepage.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['readme_text'] = open("README.md").read()
        return self.render_to_response(context)
