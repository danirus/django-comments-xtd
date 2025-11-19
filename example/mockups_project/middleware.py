from django_comments_xtd.conf import settings


class MockupsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if "cscheme" in view_kwargs:
            request.session["cscheme"] = view_kwargs["cscheme"]

        if "theme" in view_kwargs:
            request.session["comments_theme"] = view_kwargs["theme"]

        theme = request.session.get("comments_theme", "")
        setattr(settings, "COMMENTS_XTD_THEME", theme)  # noqa: B010
