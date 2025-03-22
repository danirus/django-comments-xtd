from pathlib import Path

from django.views.generic import TemplateView


class HomepageView(TemplateView):
    template_name = "homepage.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        with Path("./README.md").open() as f:
            text = f.read()
        context["readme_text"] = text.split("\n", 1)[1][1:]
        return self.render_to_response(context)
