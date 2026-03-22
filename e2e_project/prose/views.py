from django.urls import reverse
from django.views.generic import DetailView

from .models import check_comments_input_allowed


class ProseDetailView(DetailView):
    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        if self.model._meta.model_name.startswith("article"):
            return ["prose/article_detail.html"]
        elif self.model._meta.model_name.startswith("story"):
            return ["prose/story_detail.html"]
        elif self.model._meta.model_name.startswith("tale"):
            return ["prose/tale_detail.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context.get("object")
        comments_input_allowed = check_comments_input_allowed(obj)
        context.update(
            {
                "next": reverse("comments-xtd-sent"),
                "comments_input_allowed": comments_input_allowed,
                "comments_cscheme": self.request.session.get("cscheme"),
                "comments_theme": self.request.session.get("comments_theme"),
            }
        )
        return context
