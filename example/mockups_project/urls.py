from django.contrib import admin
from django.contrib.auth import logout
from django.http.response import HttpResponseRedirect
from django.urls import include, path, reverse

from .views import (
    HomepageView,
    MockupView,
    bad_form_v,
    discard_comment_v,
    flag_comment_v,
    form_js_v,
    moderated_js_v,
    moderated_v,
    muted_v,
    posted_js_v,
    posted_v,
    preview_v,
    prose_v,
    published_js_v,
    react_to_comment_v,
    reply_comment_ii_v,
    reply_comment_v,
)


def path_to_template(url_path):
    return path(
        url_path,
        MockupView.as_view(
            template_name=f"fixed/{url_path}.html",
            extra_context={"title": url_path},
        ),
        name=url_path,
    )


def logout_and_redirect(url_name):
    def _redirect(request):
        response = HttpResponseRedirect(reverse(url_name))
        logout(request)
        return response

    return _redirect


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("prose.urls")),
    path("comments/", include("django_comments_xtd.urls")),
    path("user/", include("shared.users.urls")),
    # For each mockup template:
    # 1. Add an entry to the 'mockups' dict in the next url path.
    # 2. Add an entry using the `path_to_template` function.
    #
    # Example. Adding the mockup templates `light__comment_form.html` and
    # `dark__comment_form.html` consist of 2 steps:
    # * Step 1 (see 'Step 1' below) adds a dict item to the 'mockups'
    # dictionary with the urls to the light and dark schemes:
    #     {
    #         "title": "Comment form (light)",
    #         "url1": "light__comment_form",
    #         "url2": "dark__comment_form",
    #     }
    # * Step 2 (see 'Step 2' below) consist of adding the path
    # to the two templates:
    #     path_to_template("light__comment_form"),
    #     path_to_template("dark__comment_form"),
    #
    # The step 1 here above will add two homepage links to the templates.
    # While the step 2 will add the two template urls to the Django project.
    #
    path(
        "",
        HomepageView.as_view(
            extra_context={
                # Step 1. Add an entry here if it's a mockup using the default theme.
                #         Otherwise scroll to find the appropriate list.
                "default_theme_mockups": [
                    {
                        "title": "Comments not allowed",
                        "url1": "def-light--comments-not-allowed",
                        "url2": "def-dark--comments-not-allowed",
                    },
                    {
                        "title": "form.html",
                        "url1": "def-light--comment-form",
                        "url2": "def-dark--comment-form",
                    },
                    {
                        "title": "form_js.html (does logout)",
                        "url1": "logout-and-def-light--comment-form-js",
                        "url2": "logout-and-def-dark--comment-form-js",
                    },
                    {
                        "title": "preview.html level 0 (does logout)",
                        "url1": "logout-and-def-light--preview-level-0",
                        "url2": "logout-and-def-dark--preview-level-0",
                    },
                    {
                        "title": "preview.html level 1 (does logout)",
                        "url1": "logout-and-def-light--preview-level-1",
                        "url2": "logout-and-def-dark--preview-level-1",
                    },
                    {
                        "title": "reply.html (without options)",
                        "url1": "def-light--reply",
                        "url2": "def-dark--reply",
                    },
                    {
                        "title": "reply.html (with votes, flags, reactions)",
                        "url1": "def-light--reply-ii",
                        "url2": "def-dark--reply-ii",
                    },
                    {
                        "title": "bad_form.html (JS)",
                        "url1": "def-light--bad-form-part",
                        "url2": "def-dark--bad-form-part",
                    },
                    {
                        "title": "discarded.html",
                        "url1": "def-light--discarded",
                        "url2": "def-dark--discarded",
                    },
                    {
                        "title": "flag.html",
                        "url1": "def-light--flag-comment",
                        "url2": "def-dark--flag-comment",
                    },
                    {
                        "title": "moderated.html",
                        "url1": "def-light--moderated",
                        "url2": "def-dark--moderated",
                    },
                    {
                        "title": "moderated_js.html",
                        "url1": "def-light--moderated_js",
                        "url2": "def-dark--moderated_js",
                    },
                    {
                        "title": "muted.html",
                        "url1": "def-light--muted",
                        "url2": "def-dark--muted",
                    },
                    {
                        "title": "posted.html",
                        "url1": "def-light--posted",
                        "url2": "def-dark--posted",
                    },
                    {
                        "title": "posted_js.html (does logout)",
                        "url1": "logout-and-def-light--comment-posted-js",
                        "url2": "logout-and-def-dark--comment-posted-js",
                    },
                    {
                        "title": "published_js.html (requires login)",
                        "url1": "def-light--comment-published-js",
                        "url2": "def-dark--comment-published-js",
                    },
                    {
                        "title": "react.html and reacted.html",
                        "url1": "def-light--react-to-comment",
                        "url2": "def-dark--react-to-comment",
                    },
                    {
                        "title": "1 comment, level 0, options off",
                        "url1": "def-light--1-comment-level-0-options-off",
                        "url2": "def-dark--1-comment-level-0-options-off",
                    },
                    {
                        "title": "1 comment, level 0, options on",
                        "url1": "def-light--1-comment-level-0-options-on",
                        "url2": "def-dark--1-comment-level-0-options-on",
                    },
                    {
                        "title": "1 comment, level 0, options on, JS",
                        "url1": "def-light--1-comment-level-0-options-on-js",
                        "url2": "def-dark--1-comment-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, level 0, options off",
                        "url1": "def-light--n-comments-level-0-options-off",
                        "url2": "def-dark--n-comments-level-0-options-off",
                    },
                    {
                        "title": "N comments, level 0, options on",
                        "url1": "def-light--n-comments-level-0-options-on",
                        "url2": "def-dark--n-comments-level-0-options-on",
                    },
                    {
                        "title": "N comments, level 0, options on, JS",
                        "url1": "def-light--n-comments-level-0-options-on-js",
                        "url2": "def-dark--n-comments-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, levels 0-1, options off",
                        "url1": "def-light--n-comments-levels-0-1-options-off",
                        "url2": "def-dark--n-comments-levels-0-1-options-off",
                    },
                    {
                        "title": "N comments, levels 0-1, options on",
                        "url1": "def-light--n-comments-levels-0-1-options-on",
                        "url2": "def-dark--n-comments-levels-0-1-options-on",
                    },
                    {
                        "title": "N comments, levels 0-1, options on, JS",
                        "url1": "def-light--n-comments-levels-0-1-opts-on-js",
                        "url2": "def-dark--n-comments-levels-0-1-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-2, options off",
                        "url1": "def-light--n-comments-levels-0-2-options-off",
                        "url2": "def-dark--n-comments-levels-0-2-options-off",
                    },
                    {
                        "title": "N comments, levels 0-2, options on",
                        "url1": "def-light--n-comments-levels-0-2-options-on",
                        "url2": "def-dark--n-comments-levels-0-2-options-on",
                    },
                    {
                        "title": "N comments, levels 0-2, options on, JS",
                        "url1": "def-light--n-comments-levels-0-2-opts-on-js",
                        "url2": "def-dark--n-comments-levels-0-2-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-3, options off",
                        "url1": "def-light--n-comments-levels-0-3-options-off",
                        "url2": "def-dark--n-comments-levels-0-3-options-off",
                    },
                    {
                        "title": "N comments, levels 0-3, options on",
                        "url1": "def-light--n-comments-levels-0-3-options-on",
                        "url2": "def-dark--n-comments-levels-0-3-options-on",
                    },
                    {
                        "title": "N comments, levels 0-3, options on, JS",
                        "url1": "def-light--n-comments-levels-0-3-opts-on-js",
                        "url2": "def-dark--n-comments-levels-0-3-opts-on-js",
                    },
                ],
                "avatar_in_thread_theme_mockups": [
                    {
                        "title": "preview.html level 0 (does logout)",
                        "url1": "logout-and-ait-light--preview-level-0",
                        "url2": "logout-and-ait-dark--preview-level-0",
                    },
                    {
                        "title": "preview.html level 1 (does logout)",
                        "url1": "logout-and-ait-light--preview-level-1",
                        "url2": "logout-and-ait-dark--preview-level-1",
                    },
                    {
                        "title": "reply.html (without options)",
                        "url1": "ait-light--reply",
                        "url2": "ait-dark--reply",
                    },
                    {
                        "title": "reply.html (with votes, flags, reactions)",
                        "url1": "ait-light--reply-ii",
                        "url2": "ait-dark--reply-ii",
                    },
                    {
                        "title": "1 comment, level 0, options off",
                        "url1": "ait-light--1-comment-level-0-options-off",
                        "url2": "ait-dark--1-comment-level-0-options-off",
                    },
                    {
                        "title": "1 comment, level 0, options on",
                        "url1": "ait-light--1-comment-level-0-options-on",
                        "url2": "ait-dark--1-comment-level-0-options-on",
                    },
                    {
                        "title": "1 comment, level 0, options on, JS",
                        "url1": "ait-light--1-comment-level-0-options-on-js",
                        "url2": "ait-dark--1-comment-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, level 0, options off",
                        "url1": "ait-light--n-comments-level-0-options-off",
                        "url2": "ait-dark--n-comments-level-0-options-off",
                    },
                    {
                        "title": "N comments, level 0, options on",
                        "url1": "ait-light--n-comments-level-0-options-on",
                        "url2": "ait-dark--n-comments-level-0-options-on",
                    },
                    {
                        "title": "N comments, level 0, options on, JS",
                        "url1": "ait-light--n-comments-level-0-options-on-js",
                        "url2": "ait-dark--n-comments-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, levels 0-1, options off",
                        "url1": "ait-light--n-comments-levels-0-1-options-off",
                        "url2": "ait-dark--n-comments-levels-0-1-options-off",
                    },
                    {
                        "title": "N comments, levels 0-1, options on",
                        "url1": "ait-light--n-comments-levels-0-1-options-on",
                        "url2": "ait-dark--n-comments-levels-0-1-options-on",
                    },
                    {
                        "title": "N comments, levels 0-1, options on, JS",
                        "url1": "ait-light--n-comments-levels-0-1-opts-on-js",
                        "url2": "ait-dark--n-comments-levels-0-1-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-2, options off",
                        "url1": "ait-light--n-comments-levels-0-2-options-off",
                        "url2": "ait-dark--n-comments-levels-0-2-options-off",
                    },
                    {
                        "title": "N comments, levels 0-2, options on",
                        "url1": "ait-light--n-comments-levels-0-2-options-on",
                        "url2": "ait-dark--n-comments-levels-0-2-options-on",
                    },
                    {
                        "title": "N comments, levels 0-2, options on, JS",
                        "url1": "ait-light--n-comments-levels-0-2-opts-on-js",
                        "url2": "ait-dark--n-comments-levels-0-2-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-3, options off",
                        "url1": "ait-light--n-comments-levels-0-3-options-off",
                        "url2": "ait-dark--n-comments-levels-0-3-options-off",
                    },
                    {
                        "title": "N comments, levels 0-3, options on",
                        "url1": "ait-light--n-comments-levels-0-3-options-on",
                        "url2": "ait-dark--n-comments-levels-0-3-options-on",
                    },
                    {
                        "title": "N comments, levels 0-3, options on, JS",
                        "url1": "ait-light--n-comments-levels-0-3-opts-on-js",
                        "url2": "ait-dark--n-comments-levels-0-3-opts-on-js",
                    },
                ],
                "feedback_in_header_theme_mockups": [
                    {
                        "title": "preview.html level 0 (does logout)",
                        "url1": "logout-and-fih-light--preview-level-0",
                        "url2": "logout-and-fih-dark--preview-level-0",
                    },
                    {
                        "title": "preview.html level 1 (does logout)",
                        "url1": "logout-and-fih-light--preview-level-1",
                        "url2": "logout-and-fih-dark--preview-level-1",
                    },
                    {
                        "title": "reply.html (without options)",
                        "url1": "fih-light--reply",
                        "url2": "fih-dark--reply",
                    },
                    {
                        "title": "reply.html (with votes, flags, reactions)",
                        "url1": "fih-light--reply-ii",
                        "url2": "fih-dark--reply-ii",
                    },
                    {
                        "title": "1 comment, level 0, options off",
                        "url1": "fih-light--1-comment-level-0-options-off",
                        "url2": "fih-dark--1-comment-level-0-options-off",
                    },
                    {
                        "title": "1 comment, level 0, options on",
                        "url1": "fih-light--1-comment-level-0-options-on",
                        "url2": "fih-dark--1-comment-level-0-options-on",
                    },
                    {
                        "title": "1 comment, level 0, options on, JS",
                        "url1": "fih-light--1-comment-level-0-options-on-js",
                        "url2": "fih-dark--1-comment-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, level 0, options off",
                        "url1": "fih-light--n-comments-level-0-options-off",
                        "url2": "fih-dark--n-comments-level-0-options-off",
                    },
                    {
                        "title": "N comments, level 0, options on",
                        "url1": "fih-light--n-comments-level-0-options-on",
                        "url2": "fih-dark--n-comments-level-0-options-on",
                    },
                    {
                        "title": "N comments, level 0, options on, JS",
                        "url1": "fih-light--n-comments-level-0-options-on-js",
                        "url2": "fih-dark--n-comments-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, levels 0-1, options off",
                        "url1": "fih-light--n-comments-levels-0-1-options-off",
                        "url2": "fih-dark--n-comments-levels-0-1-options-off",
                    },
                    {
                        "title": "N comments, levels 0-1, options on",
                        "url1": "fih-light--n-comments-levels-0-1-options-on",
                        "url2": "fih-dark--n-comments-levels-0-1-options-on",
                    },
                    {
                        "title": "N comments, levels 0-1, options on, JS",
                        "url1": "fih-light--n-comments-levels-0-1-opts-on-js",
                        "url2": "fih-dark--n-comments-levels-0-1-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-2, options off",
                        "url1": "fih-light--n-comments-levels-0-2-options-off",
                        "url2": "fih-dark--n-comments-levels-0-2-options-off",
                    },
                    {
                        "title": "N comments, levels 0-2, options on",
                        "url1": "fih-light--n-comments-levels-0-2-options-on",
                        "url2": "fih-dark--n-comments-levels-0-2-options-on",
                    },
                    {
                        "title": "N comments, levels 0-2, options on, JS",
                        "url1": "fih-light--n-comments-levels-0-2-opts-on-js",
                        "url2": "fih-dark--n-comments-levels-0-2-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-3, options off",
                        "url1": "fih-light--n-comments-levels-0-3-options-off",
                        "url2": "fih-dark--n-comments-levels-0-3-options-off",
                    },
                    {
                        "title": "N comments, levels 0-3, options on",
                        "url1": "fih-light--n-comments-levels-0-3-options-on",
                        "url2": "fih-dark--n-comments-levels-0-3-options-on",
                    },
                    {
                        "title": "N comments, levels 0-3, options on, JS",
                        "url1": "fih-light--n-comments-levels-0-3-opts-on-js",
                        "url2": "fih-dark--n-comments-levels-0-3-opts-on-js",
                    },
                ],
                "avatar_in_header_theme_mockups": [
                    {
                        "title": "preview.html level 0 (does logout)",
                        "url1": "logout-and-aih-light--preview-level-0",
                        "url2": "logout-and-aih-dark--preview-level-0",
                    },
                    {
                        "title": "preview.html level 1 (does logout)",
                        "url1": "logout-and-aih-light--preview-level-1",
                        "url2": "logout-and-aih-dark--preview-level-1",
                    },
                    {
                        "title": "reply.html (without options)",
                        "url1": "aih-light--reply",
                        "url2": "aih-dark--reply",
                    },
                    {
                        "title": "reply.html (with votes, flags, reactions)",
                        "url1": "aih-light--reply-ii",
                        "url2": "aih-dark--reply-ii",
                    },
                    {
                        "title": "1 comment, level 0, options off",
                        "url1": "aih-light--1-comment-level-0-options-off",
                        "url2": "aih-dark--1-comment-level-0-options-off",
                    },
                    {
                        "title": "1 comment, level 0, options on",
                        "url1": "aih-light--1-comment-level-0-options-on",
                        "url2": "aih-dark--1-comment-level-0-options-on",
                    },
                    {
                        "title": "1 comment, level 0, options on, JS",
                        "url1": "aih-light--1-comment-level-0-options-on-js",
                        "url2": "aih-dark--1-comment-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, level 0, options off",
                        "url1": "aih-light--n-comments-level-0-options-off",
                        "url2": "aih-dark--n-comments-level-0-options-off",
                    },
                    {
                        "title": "N comments, level 0, options on",
                        "url1": "aih-light--n-comments-level-0-options-on",
                        "url2": "aih-dark--n-comments-level-0-options-on",
                    },
                    {
                        "title": "N comments, level 0, options on, JS",
                        "url1": "aih-light--n-comments-level-0-options-on-js",
                        "url2": "aih-dark--n-comments-level-0-options-on-js",
                    },
                    {
                        "title": "N comments, levels 0-1, options off",
                        "url1": "aih-light--n-comments-levels-0-1-options-off",
                        "url2": "aih-dark--n-comments-levels-0-1-options-off",
                    },
                    {
                        "title": "N comments, levels 0-1, options on",
                        "url1": "aih-light--n-comments-levels-0-1-options-on",
                        "url2": "aih-dark--n-comments-levels-0-1-options-on",
                    },
                    {
                        "title": "N comments, levels 0-1, options on, JS",
                        "url1": "aih-light--n-comments-levels-0-1-opts-on-js",
                        "url2": "aih-dark--n-comments-levels-0-1-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-2, options off",
                        "url1": "aih-light--n-comments-levels-0-2-options-off",
                        "url2": "aih-dark--n-comments-levels-0-2-options-off",
                    },
                    {
                        "title": "N comments, levels 0-2, options on",
                        "url1": "aih-light--n-comments-levels-0-2-options-on",
                        "url2": "aih-dark--n-comments-levels-0-2-options-on",
                    },
                    {
                        "title": "N comments, levels 0-2, options on, JS",
                        "url1": "aih-light--n-comments-levels-0-2-opts-on-js",
                        "url2": "aih-dark--n-comments-levels-0-2-opts-on-js",
                    },
                    {
                        "title": "N comments, levels 0-3, options off",
                        "url1": "aih-light--n-comments-levels-0-3-options-off",
                        "url2": "aih-dark--n-comments-levels-0-3-options-off",
                    },
                    {
                        "title": "N comments, levels 0-3, options on",
                        "url1": "aih-light--n-comments-levels-0-3-options-on",
                        "url2": "aih-dark--n-comments-levels-0-3-options-on",
                    },
                    {
                        "title": "N comments, levels 0-3, options on, JS",
                        "url1": "aih-light--n-comments-levels-0-3-opts-on-js",
                        "url2": "aih-dark--n-comments-levels-0-3-opts-on-js",
                    },
                ],
                "fixed": [
                    {
                        "title": "default theme, levels 0-1, options off",
                        "url1": "defn_light__n_comments_levels_0_1_options_off",
                        "url2": "defn_dark__n_comments_levels_0_1_options_off",
                    },
                    {
                        "title": "default theme, levels 0-2, options off",
                        "url1": "defn_light__n_comments_levels_0_2_options_off",
                        "url2": "defn_dark__n_comments_levels_0_2_options_off",
                    },
                    {
                        "title": "default theme, levels 0-3, options off",
                        "url1": "defn_light__n_comments_levels_0_3_options_off",
                        "url2": "defn_dark__n_comments_levels_0_3_options_off",
                    },
                    {
                        "title": "avatar_in_thread, levels 0-1, options off",
                        "url1": "aitn_light__n_comments_levels_0_1_options_off",
                        "url2": "aitn_dark__n_comments_levels_0_1_options_off",
                    },
                    {
                        "title": "avatar_in_thread, levels 0-2, options off",
                        "url1": "aitn_light__n_comments_levels_0_2_options_off",
                        "url2": "aitn_dark__n_comments_levels_0_2_options_off",
                    },
                    {
                        "title": "avatar_in_thread, levels 0-3, options off",
                        "url1": "aitn_light__n_comments_levels_0_3_options_off",
                        "url2": "aitn_dark__n_comments_levels_0_3_options_off",
                    },
                    {
                        "title": "feedback_in_header, levels 0-1, options off",
                        "url1": "fihn_light__n_comments_levels_0_1_options_off",
                        "url2": "fihn_dark__n_comments_levels_0_1_options_off",
                    },
                    {
                        "title": "feedback_in_header, levels 0-2, options off",
                        "url1": "fihn_light__n_comments_levels_0_2_options_off",
                        "url2": "fihn_dark__n_comments_levels_0_2_options_off",
                    },
                    {
                        "title": "feedback_in_header, levels 0-3, options off",
                        "url1": "fihn_light__n_comments_levels_0_3_options_off",
                        "url2": "fihn_dark__n_comments_levels_0_3_options_off",
                    },
                    {
                        "title": "avatar_in_header, levels 0-1, options off",
                        "url1": "aihn_light__n_comments_levels_0_1_options_off",
                        "url2": "aihn_dark__n_comments_levels_0_1_options_off",
                    },
                    {
                        "title": "avatar_in_header, levels 0-2, options off",
                        "url1": "aihn_light__n_comments_levels_0_2_options_off",
                        "url2": "aihn_dark__n_comments_levels_0_2_options_off",
                    },
                    {
                        "title": "avatar_in_header, levels 0-3, options off",
                        "url1": "aihn_light__n_comments_levels_0_3_options_off",
                        "url2": "aihn_dark__n_comments_levels_0_3_options_off",
                    },
                ],
            }
        ),
        name="homepage",
    ),
    # -----------------------------------------------------
    # Step 2. Add an entry here below.
    # ----------------------
    # Default theme mockups.
    path(
        "def-light--comments-not-allowed",
        prose_v("ArticleCommentsL0", "comments-not-allowed", "light"),
        name="def-light--comments-not-allowed",
    ),
    path(
        "def-dark--comments-not-allowed",
        prose_v("ArticleCommentsL0", "comments-not-allowed", "dark"),
        name="def-dark--comments-not-allowed",
    ),
    path(
        "def-light--comment-form",
        prose_v("ArticleCommentsL0", "comment-form", "light"),
        name="def-light--comment-form",
    ),
    path(
        "def-dark--comment-form",
        prose_v("ArticleCommentsL0", "comment-form", "dark"),
        name="def-dark--comment-form",
    ),
    # -------------------------------------------
    path(
        "def-light--comment-form_js",
        form_js_v("force-form-js", "light"),
        name="def-light--comment-form_js",
    ),
    path(
        "def-dark--comment-form_js",
        form_js_v("force-form-js", "dark"),
        name="def-dark--comment-form_js",
    ),
    path(
        "logout-and-def-light--comment-form-js",
        logout_and_redirect("def-light--comment-form_js"),
        name="logout-and-def-light--comment-form-js",
    ),
    path(
        "logout-and-def-dark--comment-form-js",
        logout_and_redirect("def-dark--comment-form_js"),
        name="logout-and-def-dark--comment-form-js",
    ),
    # -------------------------------------------
    path(
        "def_light__preview_level_0",
        preview_v("light", reply_to=0),
        name="def_light__preview_level_0",
    ),
    path(
        "def_dark__preview_level_0",
        preview_v("dark", reply_to=0),
        name="def_dark__preview_level_0",
    ),
    path(
        "logout-and-def-light--preview-level-0",
        logout_and_redirect("def_light__preview_level_0"),
        name="logout-and-def-light--preview-level-0",
    ),
    path(
        "logout-and-def-dark--preview-level-0",
        logout_and_redirect("def_dark__preview_level_0"),
        name="logout-and-def-dark--preview-level-0",
    ),
    # -------------------------------------------
    path(
        "def_light__preview_level_1",
        preview_v("light", reply_to=1),
        name="def_light__preview_level_1",
    ),
    path(
        "def_dark__preview_level_1",
        preview_v("dark", reply_to=1),
        name="def_dark__preview_level_1",
    ),
    path(
        "logout-and-def-light--preview-level-1",
        logout_and_redirect("def_light__preview_level_1"),
        name="logout-and-def-light--preview-level-1",
    ),
    path(
        "logout-and-def-dark--preview-level-1",
        logout_and_redirect("def_dark__preview_level_1"),
        name="logout-and-def-dark--preview-level-1",
    ),
    # -------------------------------------------
    path("def-light--reply", reply_comment_v("light"), name="def-light--reply"),
    path("def-dark--reply", reply_comment_v("dark"), name="def-dark--reply"),
    path(
        "def-light--reply-ii",
        reply_comment_ii_v("light"),
        name="def-light--reply-ii",
    ),
    path(
        "def-dark--reply-ii",
        reply_comment_ii_v("dark"),
        name="def-dark--reply-ii",
    ),
    path(
        "def-light--bad-form-part",
        bad_form_v("force-bad-form", "light"),
        name="def-light--bad-form-part",
    ),
    path(
        "def-dark--bad-form-part",
        bad_form_v("force-bad-form", "dark"),
        name="def-dark--bad-form-part",
    ),
    path(
        "def-light--discarded",
        discard_comment_v("light"),
        name="def-light--discarded",
    ),
    path(
        "def-dark--discarded",
        discard_comment_v("dark"),
        name="def-dark--discarded",
    ),
    path(
        "def-light--flag-comment",
        flag_comment_v("light"),
        name="def-light--flag-comment",
    ),
    path(
        "def-dark--flag-comment",
        flag_comment_v("dark"),
        name="def-dark--flag-comment",
    ),
    path(
        "def-light--moderated",
        moderated_v("light"),
        name="def-light--moderated",
    ),
    path(
        "def-dark--moderated", moderated_v("dark"), name="def-dark--moderated"
    ),
    path(
        "def-light--moderated_js",
        moderated_js_v("force-moderated-js", "light"),
        name="def-light--moderated_js",
    ),
    path(
        "def-dark--moderated_js",
        moderated_js_v("force-moderated-js", "dark"),
        name="def-dark--moderated_js",
    ),
    path("def-light--muted", muted_v("light"), name="def-light--muted"),
    path("def-dark--muted", muted_v("dark"), name="def-dark--muted"),
    path("def-light--posted", posted_v("light"), name="def-light--posted"),
    path("def-dark--posted", posted_v("dark"), name="def-dark--posted"),
    # --------------------------------------------
    path(
        "def_light__comment_posted_js",
        posted_js_v("force-posted-js", "light"),
        name="def_light__comment_posted_js",
    ),
    path(
        "def_dark__comment_posted_js",
        posted_js_v("force-posted-js", "dark"),
        name="def_dark__comment_posted_js",
    ),
    path(
        "logout-and-def-light--comment-posted-js",
        logout_and_redirect("def_light__comment_posted_js"),
        name="logout-and-def-light--comment-posted-js",
    ),
    path(
        "logout-and-def-dark--comment-posted-js",
        logout_and_redirect("def_dark__comment_posted_js"),
        name="logout-and-def-dark--comment-posted-js",
    ),
    path(
        "def-light--comment-published-js",
        published_js_v("force-published-js", "light"),
        name="def-light--comment-published-js",
    ),
    path(
        "def-dark--comment-published-js",
        published_js_v("force-published-js", "dark"),
        name="def-dark--comment-published-js",
    ),
    # --------------------------------------------
    path(
        "def-light--react-to-comment",
        react_to_comment_v("light"),
        name="def-light--react-to-comment",
    ),
    path(
        "def-dark--react-to-comment",
        react_to_comment_v("dark"),
        name="def-dark--react-to-comment",
    ),
    # ----------------------
    # -- 1 comment, level 0
    # -- options off
    path(
        "def-light--1-comment-level-0-options-off",
        prose_v("ArticleCommentsL0", "one-comment-options-off", "light"),
        name="def-light--1-comment-level-0-options-off",
    ),
    path(
        "def-dark--1-comment-level-0-options-off",
        prose_v("ArticleCommentsL0", "one-comment-options-off", "dark"),
        name="def-dark--1-comment-level-0-options-off",
    ),
    # -- options on
    path(
        "def-light--1-comment-level-0-options-on",
        prose_v("StoryCommentsL0", "one-comment-options-on", "light"),
        name="def-light--1-comment-level-0-options-on",
    ),
    path(
        "def-dark--1-comment-level-0-options-on",
        prose_v("StoryCommentsL0", "one-comment-options-on", "dark"),
        name="def-dark--1-comment-level-0-options-on",
    ),
    # -- options on-js
    path(
        "def-light--1-comment-level-0-options-on-js",
        prose_v("TaleCommentsL0", "one-comment-options-on-js", "light"),
        name="def-light--1-comment-level-0-options-on-js",
    ),
    path(
        "def-dark--1-comment-level-0-options-on-js",
        prose_v("TaleCommentsL0", "one-comment-options-on-js", "dark"),
        name="def-dark--1-comment-level-0-options-on-js",
    ),
    # -----------------------------
    # -- n-comments, level 0
    # -- options off
    path(
        "def-light--n-comments-level-0-options-off",
        prose_v("ArticleCommentsL0", "n-comments-options-off", "light"),
        name="def-light--n-comments-level-0-options-off",
    ),
    path(
        "def-dark--n-comments-level-0-options-off",
        prose_v("ArticleCommentsL0", "n-comments-options-off", "dark"),
        name="def-dark--n-comments-level-0-options-off",
    ),
    # -- options on
    path(
        "def-light--n-comments-level-0-options-on",
        prose_v("StoryCommentsL0", "n-comments-options-on", "light"),
        name="def-light--n-comments-level-0-options-on",
    ),
    path(
        "def-dark--n-comments-level-0-options-on",
        prose_v("StoryCommentsL0", "n-comments-options-on", "dark"),
        name="def-dark--n-comments-level-0-options-on",
    ),
    # -- options on-js
    path(
        "def-light--n-comments-level-0-options-on-js",
        prose_v("TaleCommentsL0", "n-comments-options-on-js", "light"),
        name="def-light--n-comments-level-0-options-on-js",
    ),
    path(
        "def-dark--n-comments-level-0-options-on-js",
        prose_v("TaleCommentsL0", "n-comments-options-on-js", "dark"),
        name="def-dark--n-comments-level-0-options-on-js",
    ),
    # -----------------------------
    # -- n-comments, levels 0-1
    # -- options off
    path(
        "def-light--n-comments-levels-0-1-options-off",
        prose_v("ArticleCommentsL1", "n-comments-options-off", "light"),
        name="def-light--n-comments-levels-0-1-options-off",
    ),
    path(
        "def-dark--n-comments-levels-0-1-options-off",
        prose_v("ArticleCommentsL1", "n-comments-options-off", "dark"),
        name="def-dark--n-comments-levels-0-1-options-off",
    ),
    # -- options on
    path(
        "def-light--n-comments-levels-0-1-options-on",
        prose_v("StoryCommentsL1", "n-comments-options-on", "light"),
        name="def-light--n-comments-levels-0-1-options-on",
    ),
    path(
        "def-dark--n-comments-levels-0-1-options-on",
        prose_v("StoryCommentsL1", "n-comments-options-on", "dark"),
        name="def-dark--n-comments-levels-0-1-options-on",
    ),
    # -- options on-js
    path(
        "def-light--n-comments-levels-0-1-opts-on-js",
        prose_v("TaleCommentsL1", "n-comments-options-on-js", "light"),
        name="def-light--n-comments-levels-0-1-opts-on-js",
    ),
    path(
        "def-dark--n-comments-levels-0-1-opts-on-js",
        prose_v("TaleCommentsL1", "n-comments-options-on-js", "dark"),
        name="def-dark--n-comments-levels-0-1-opts-on-js",
    ),
    # -----------------------------
    # -- n-comments, levels 0-2
    # -- options off
    path(
        "def-light--n-comments-levels-0-2-options-off",
        prose_v("ArticleCommentsL2", "n-comments-options-off", "light"),
        name="def-light--n-comments-levels-0-2-options-off",
    ),
    path(
        "def-dark--n-comments-levels-0-2-options-off",
        prose_v("ArticleCommentsL2", "n-comments-options-off", "dark"),
        name="def-dark--n-comments-levels-0-2-options-off",
    ),
    # -- options on
    path(
        "def-light--n-comments-levels-0-2-options-on",
        prose_v("StoryCommentsL2", "n-comments-options-on", "light"),
        name="def-light--n-comments-levels-0-2-options-on",
    ),
    path(
        "def-dark--n-comments-levels-0-2-options-on",
        prose_v("StoryCommentsL2", "n-comments-options-on", "dark"),
        name="def-dark--n-comments-levels-0-2-options-on",
    ),
    # -- options on-js
    path(
        "def-light--n-comments-levels-0-2-opts-on-js",
        prose_v("TaleCommentsL2", "n-comments-options-on-js", "light"),
        name="def-light--n-comments-levels-0-2-opts-on-js",
    ),
    path(
        "def-dark--n-comments-levels-0-2-opts-on-js",
        prose_v("TaleCommentsL2", "n-comments-options-on-js", "dark"),
        name="def-dark--n-comments-levels-0-2-opts-on-js",
    ),
    # -----------------------------
    # -- n-comments, levels 0-3
    # -- options off
    path(
        "def-light--n-comments-levels-0-3-options-off",
        prose_v("ArticleCommentsL3", "n-comments-options-off", "light"),
        name="def-light--n-comments-levels-0-3-options-off",
    ),
    path(
        "def-dark--n-comments-levels-0-3-options-off",
        prose_v("ArticleCommentsL3", "n-comments-options-off", "dark"),
        name="def-dark--n-comments-levels-0-3-options-off",
    ),
    # -- options on
    path(
        "def-light--n-comments-levels-0-3-options-on",
        prose_v("StoryCommentsL3", "n-comments-options-on", "light"),
        name="def-light--n-comments-levels-0-3-options-on",
    ),
    path(
        "def-dark--n-comments-levels-0-3-options-on",
        prose_v("StoryCommentsL3", "n-comments-options-on", "dark"),
        name="def-dark--n-comments-levels-0-3-options-on",
    ),
    # -- options on-js
    path(
        "def-light--n-comments-levels-0-3-opts-on-js",
        prose_v("TaleCommentsL3", "n-comments-options-on-js", "light"),
        name="def-light--n-comments-levels-0-3-opts-on-js",
    ),
    path(
        "def-dark--n-comments-levels-0-3-opts-on-js",
        prose_v("TaleCommentsL3", "n-comments-options-on-js", "dark"),
        name="def-dark--n-comments-levels-0-3-opts-on-js",
    ),
    ###########################
    # avatar_in_thread mockups.
    path(
        "ait_light__preview_level_0",
        preview_v("light", theme="avatar_in_thread", reply_to=0),
        name="ait_light__preview_level_0",
    ),
    path(
        "ait_dark__preview_level_0",
        preview_v("dark", theme="avatar_in_thread", reply_to=0),
        name="ait_dark__preview_level_0",
    ),
    path(
        "logout-and-ait-light--preview-level-0",
        logout_and_redirect("ait_light__preview_level_0"),
        name="logout-and-ait-light--preview-level-0",
    ),
    path(
        "logout-and-ait-dark--preview-level-0",
        logout_and_redirect("ait_dark__preview_level_0"),
        name="logout-and-ait-dark--preview-level-0",
    ),
    # -------------------------------------------
    path(
        "ait_light__preview_level_1",
        preview_v("light", theme="avatar_in_thread", reply_to=1),
        name="ait_light__preview_level_1",
    ),
    path(
        "ait_dark__preview_level_1",
        preview_v("dark", theme="avatar_in_thread", reply_to=1),
        name="ait_dark__preview_level_1",
    ),
    path(
        "logout-and-ait-light--preview-level-1",
        logout_and_redirect("ait_light__preview_level_1"),
        name="logout-and-ait-light--preview-level-1",
    ),
    path(
        "logout-and-ait-dark--preview-level-1",
        logout_and_redirect("ait_dark__preview_level_1"),
        name="logout-and-ait-dark--preview-level-1",
    ),
    # -------------------------------------------
    # Reply comment, avatar_in_thread.
    #
    path(
        "ait-light--reply",
        reply_comment_v("light", theme="avatar_in_thread"),
        name="ait-light--reply",
    ),
    path(
        "ait-dark--reply",
        reply_comment_v("dark", theme="avatar_in_thread"),
        name="ait-dark--reply",
    ),
    path(
        "ait-light--reply-ii",
        reply_comment_ii_v("light", theme="avatar_in_thread"),
        name="ait-light--reply-ii",
    ),
    path(
        "ait-dark--reply-ii",
        reply_comment_ii_v("dark", theme="avatar_in_thread"),
        name="ait-dark--reply-ii",
    ),
    # ----------------------
    # -- 1 comment, level 0
    # -- options off
    path(
        "ait-light--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--1-comment-level-0-options-off",
    ),
    path(
        "ait-dark--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--1-comment-level-0-options-off",
    ),
    # -- options on
    path(
        "ait-light--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--1-comment-level-0-options-on",
    ),
    path(
        "ait-dark--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--1-comment-level-0-options-on",
    ),
    # -- options on-js
    path(
        "ait-light--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--1-comment-level-0-options-on-js",
    ),
    path(
        "ait-dark--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--1-comment-level-0-options-on-js",
    ),
    # ------------------------------------------
    # -- avatar_in_thread, comment list, level 0
    path(
        "ait-light--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-level-0-options-off",
    ),
    path(
        "ait-dark--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-level-0-options-off",
    ),
    path(
        "ait-light--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-level-0-options-on",
    ),
    path(
        "ait-dark--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-level-0-options-on",
    ),
    # -- options on-js
    path(
        "ait-light--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-level-0-options-on-js",
    ),
    path(
        "ait-dark--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-level-0-options-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_thread, comment list, levels 0-1
    path(
        "ait-light--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-1-options-off",
    ),
    path(
        "ait-dark--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-1-options-off",
    ),
    path(
        "ait-light--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-1-options-on",
    ),
    path(
        "ait-dark--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-1-options-on",
    ),
    # -- options on-js
    path(
        "ait-light--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-1-opts-on-js",
    ),
    path(
        "ait-dark--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-1-opts-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_thread, comment list, levels 0-2
    path(
        "ait-light--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-2-options-off",
    ),
    path(
        "ait-dark--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-2-options-off",
    ),
    path(
        "ait-light--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-2-options-on",
    ),
    path(
        "ait-dark--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-2-options-on",
    ),
    # -- options on-js
    path(
        "ait-light--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-2-opts-on-js",
    ),
    path(
        "ait-dark--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-2-opts-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_thread, comment list, levels 0-3
    path(
        "ait-light--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-3-options-off",
    ),
    path(
        "ait-dark--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-3-options-off",
    ),
    path(
        "ait-light--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-3-options-on",
    ),
    path(
        "ait-dark--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-3-options-on",
    ),
    # -- options on-js
    path(
        "ait-light--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_thread",
        ),
        name="ait-light--n-comments-levels-0-3-opts-on-js",
    ),
    path(
        "ait-dark--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_thread",
        ),
        name="ait-dark--n-comments-levels-0-3-opts-on-js",
    ),
    # ##########################
    # feedback_in_header mockups.
    path(
        "fih_light__preview_level_0",
        preview_v("light", theme="feedback_in_header", reply_to=0),
        name="fih_light__preview_level_0",
    ),
    path(
        "fih_dark__preview_level_0",
        preview_v("dark", theme="feedback_in_header", reply_to=0),
        name="fih_dark__preview_level_0",
    ),
    path(
        "logout-and-fih-light--preview-level-0",
        logout_and_redirect("fih_light__preview_level_0"),
        name="logout-and-fih-light--preview-level-0",
    ),
    path(
        "logout-and-fih-dark--preview-level-0",
        logout_and_redirect("fih_dark__preview_level_0"),
        name="logout-and-fih-dark--preview-level-0",
    ),
    # -------------------------------------------
    path(
        "fih_light__preview_level_1",
        preview_v("light", theme="feedback_in_header", reply_to=1),
        name="fih_light__preview_level_1",
    ),
    path(
        "fih_dark__preview_level_1",
        preview_v("dark", theme="feedback_in_header", reply_to=1),
        name="fih_dark__preview_level_1",
    ),
    path(
        "logout-and-fih-light--preview-level-1",
        logout_and_redirect("fih_light__preview_level_1"),
        name="logout-and-fih-light--preview-level-1",
    ),
    path(
        "logout-and-fih-dark--preview-level-1",
        logout_and_redirect("fih_dark__preview_level_1"),
        name="logout-and-fih-dark--preview-level-1",
    ),
    # -------------------------------------------
    # Reply comment, feedback_in_header.
    #
    path(
        "fih-light--reply",
        reply_comment_v("light", theme="feedback_in_header"),
        name="fih-light--reply",
    ),
    path(
        "fih-dark--reply",
        reply_comment_v("dark", theme="feedback_in_header"),
        name="fih-dark--reply",
    ),
    path(
        "fih-light--reply-ii",
        reply_comment_ii_v("light", theme="feedback_in_header"),
        name="fih-light--reply-ii",
    ),
    path(
        "fih-dark--reply-ii",
        reply_comment_ii_v("dark", theme="feedback_in_header"),
        name="fih-dark--reply-ii",
    ),
    # ----------------------
    # -- 1 comment, level 0
    # -- options off
    path(
        "fih-light--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--1-comment-level-0-options-off",
    ),
    path(
        "fih-dark--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--1-comment-level-0-options-off",
    ),
    path(
        "fih-light--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--1-comment-level-0-options-on",
    ),
    path(
        "fih-dark--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--1-comment-level-0-options-on",
    ),
    # -- options on-js
    path(
        "fih-light--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--1-comment-level-0-options-on-js",
    ),
    path(
        "fih-dark--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--1-comment-level-0-options-on-js",
    ),
    # ------------------------------------------
    # -- feedback_in_header, comment list, level 0
    path(
        "fih-light--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-level-0-options-off",
    ),
    path(
        "fih-dark--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-level-0-options-off",
    ),
    path(
        "fih-light--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-level-0-options-on",
    ),
    path(
        "fih-dark--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-level-0-options-on",
    ),
    # -- options on-js
    path(
        "fih-light--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-level-0-options-on-js",
    ),
    path(
        "fih-dark--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-level-0-options-on-js",
    ),
    # ---------------------------------------------
    # -- feedback_in_header, comment list, levels 0-1
    path(
        "fih-light--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-1-options-off",
    ),
    path(
        "fih-dark--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-1-options-off",
    ),
    path(
        "fih-light--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-1-options-on",
    ),
    path(
        "fih-dark--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-1-options-on",
    ),
    # -- options on-js
    path(
        "fih-light--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-1-opts-on-js",
    ),
    path(
        "fih-dark--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-1-opts-on-js",
    ),
    # ---------------------------------------------
    # -- feedback_in_header, comment list, levels 0-2
    path(
        "fih-light--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-2-options-off",
    ),
    path(
        "fih-dark--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-2-options-off",
    ),
    path(
        "fih-light--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-2-options-on",
    ),
    path(
        "fih-dark--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-2-options-on",
    ),
    # -- options on-js
    path(
        "fih-light--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-2-opts-on-js",
    ),
    path(
        "fih-dark--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-2-opts-on-js",
    ),
    # ---------------------------------------------
    # -- feedback_in_header, comment list, levels 0-3
    path(
        "fih-light--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-3-options-off",
    ),
    path(
        "fih-dark--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-3-options-off",
    ),
    path(
        "fih-light--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-3-options-on",
    ),
    path(
        "fih-dark--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-3-options-on",
    ),
    # -- options on-js
    path(
        "fih-light--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "light",
            theme="feedback_in_header",
        ),
        name="fih-light--n-comments-levels-0-3-opts-on-js",
    ),
    path(
        "fih-dark--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "dark",
            theme="feedback_in_header",
        ),
        name="fih-dark--n-comments-levels-0-3-opts-on-js",
    ),
    # ##########################
    # avatar_in_header mockups.
    path(
        "aih_light__preview_level_0",
        preview_v("light", theme="avatar_in_header", reply_to=0),
        name="aih_light__preview_level_0",
    ),
    path(
        "aih_dark__preview_level_0",
        preview_v("dark", theme="avatar_in_header", reply_to=0),
        name="aih_dark__preview_level_0",
    ),
    path(
        "logout-and-aih-light--preview-level-0",
        logout_and_redirect("aih_light__preview_level_0"),
        name="logout-and-aih-light--preview-level-0",
    ),
    path(
        "logout-and-aih-dark--preview-level-0",
        logout_and_redirect("aih_dark__preview_level_0"),
        name="logout-and-aih-dark--preview-level-0",
    ),
    # -------------------------------------------
    path(
        "aih_light__preview_level_1",
        preview_v("light", theme="avatar_in_header", reply_to=1),
        name="aih_light__preview_level_1",
    ),
    path(
        "aih_dark__preview_level_1",
        preview_v("dark", theme="avatar_in_header", reply_to=1),
        name="aih_dark__preview_level_1",
    ),
    path(
        "logout-and-aih-light--preview-level-1",
        logout_and_redirect("aih_light__preview_level_1"),
        name="logout-and-aih-light--preview-level-1",
    ),
    path(
        "logout-and-aih-dark--preview-level-1",
        logout_and_redirect("aih_dark__preview_level_1"),
        name="logout-and-aih-dark--preview-level-1",
    ),
    # -------------------------------------------
    # Reply comment, avatar_in_header.
    #
    path(
        "aih-light--reply",
        reply_comment_v("light", theme="avatar_in_header"),
        name="aih-light--reply",
    ),
    path(
        "aih-dark--reply",
        reply_comment_v("dark", theme="avatar_in_header"),
        name="aih-dark--reply",
    ),
    path(
        "aih-light--reply-ii",
        reply_comment_ii_v("light", theme="avatar_in_header"),
        name="aih-light--reply-ii",
    ),
    path(
        "aih-dark--reply-ii",
        reply_comment_ii_v("dark", theme="avatar_in_header"),
        name="aih-dark--reply-ii",
    ),
    # ----------------------
    # -- 1 comment, level 0
    # -- options off
    path(
        "aih-light--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--1-comment-level-0-options-off",
    ),
    path(
        "aih-dark--1-comment-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "one-comment-options-off",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--1-comment-level-0-options-off",
    ),
    path(
        "aih-light--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--1-comment-level-0-options-on",
    ),
    path(
        "aih-dark--1-comment-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "one-comment-options-on",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--1-comment-level-0-options-on",
    ),
    # -- options on-js
    path(
        "aih-light--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--1-comment-level-0-options-on-js",
    ),
    path(
        "aih-dark--1-comment-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "one-comment-options-on-js",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--1-comment-level-0-options-on-js",
    ),
    # ------------------------------------------
    # -- avatar_in_header, comment list, level 0
    path(
        "aih-light--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-level-0-options-off",
    ),
    path(
        "aih-dark--n-comments-level-0-options-off",
        prose_v(
            "ArticleCommentsL0",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-level-0-options-off",
    ),
    path(
        "aih-light--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-level-0-options-on",
    ),
    path(
        "aih-dark--n-comments-level-0-options-on",
        prose_v(
            "StoryCommentsL0",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-level-0-options-on",
    ),
    # -- options on-js
    path(
        "aih-light--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-level-0-options-on-js",
    ),
    path(
        "aih-dark--n-comments-level-0-options-on-js",
        prose_v(
            "TaleCommentsL0",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-level-0-options-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_header, comment list, levels 0-1
    path(
        "aih-light--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-1-options-off",
    ),
    path(
        "aih-dark--n-comments-levels-0-1-options-off",
        prose_v(
            "ArticleCommentsL1",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-1-options-off",
    ),
    path(
        "aih-light--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-1-options-on",
    ),
    path(
        "aih-dark--n-comments-levels-0-1-options-on",
        prose_v(
            "StoryCommentsL1",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-1-options-on",
    ),
    # -- options on-js
    path(
        "aih-light--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-1-opts-on-js",
    ),
    path(
        "aih-dark--n-comments-levels-0-1-opts-on-js",
        prose_v(
            "TaleCommentsL1",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-1-opts-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_header, comment list, levels 0-2
    path(
        "aih-light--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-2-options-off",
    ),
    path(
        "aih-dark--n-comments-levels-0-2-options-off",
        prose_v(
            "ArticleCommentsL2",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-2-options-off",
    ),
    path(
        "aih-light--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-2-options-on",
    ),
    path(
        "aih-dark--n-comments-levels-0-2-options-on",
        prose_v(
            "StoryCommentsL2",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-2-options-on",
    ),
    # -- options on-js
    path(
        "aih-light--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-2-opts-on-js",
    ),
    path(
        "aih-dark--n-comments-levels-0-2-opts-on-js",
        prose_v(
            "TaleCommentsL2",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-2-opts-on-js",
    ),
    # ---------------------------------------------
    # -- avatar_in_header, comment list, levels 0-3
    path(
        "aih-light--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-3-options-off",
    ),
    path(
        "aih-dark--n-comments-levels-0-3-options-off",
        prose_v(
            "ArticleCommentsL3",
            "n-comments-options-off",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-3-options-off",
    ),
    path(
        "aih-light--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-3-options-on",
    ),
    path(
        "aih-dark--n-comments-levels-0-3-options-on",
        prose_v(
            "StoryCommentsL3",
            "n-comments-options-on",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-3-options-on",
    ),
    # -- options on-js
    path(
        "aih-light--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "light",
            theme="avatar_in_header",
        ),
        name="aih-light--n-comments-levels-0-3-opts-on-js",
    ),
    path(
        "aih-dark--n-comments-levels-0-3-opts-on-js",
        prose_v(
            "TaleCommentsL3",
            "n-comments-options-on-js",
            "dark",
            theme="avatar_in_header",
        ),
        name="aih-dark--n-comments-levels-0-3-opts-on-js",
    ),
    # ##########################
    # Almost pure HTML mockups.
    path_to_template("defn_light__n_comments_levels_0_1_options_off"),
    path_to_template("defn_dark__n_comments_levels_0_1_options_off"),
    path_to_template("aitn_light__n_comments_levels_0_1_options_off"),
    path_to_template("aitn_dark__n_comments_levels_0_1_options_off"),
    path_to_template("fihn_light__n_comments_levels_0_1_options_off"),
    path_to_template("fihn_dark__n_comments_levels_0_1_options_off"),
    path_to_template("aihn_light__n_comments_levels_0_1_options_off"),
    path_to_template("aihn_dark__n_comments_levels_0_1_options_off"),
    path_to_template("defn_light__n_comments_levels_0_2_options_off"),
    path_to_template("defn_dark__n_comments_levels_0_2_options_off"),
    path_to_template("aitn_light__n_comments_levels_0_2_options_off"),
    path_to_template("aitn_dark__n_comments_levels_0_2_options_off"),
    path_to_template("fihn_light__n_comments_levels_0_2_options_off"),
    path_to_template("fihn_dark__n_comments_levels_0_2_options_off"),
    path_to_template("aihn_light__n_comments_levels_0_2_options_off"),
    path_to_template("aihn_dark__n_comments_levels_0_2_options_off"),
    path_to_template("defn_light__n_comments_levels_0_3_options_off"),
    path_to_template("defn_dark__n_comments_levels_0_3_options_off"),
    path_to_template("aitn_light__n_comments_levels_0_3_options_off"),
    path_to_template("aitn_dark__n_comments_levels_0_3_options_off"),
    path_to_template("fihn_light__n_comments_levels_0_3_options_off"),
    path_to_template("fihn_dark__n_comments_levels_0_3_options_off"),
    path_to_template("aihn_light__n_comments_levels_0_3_options_off"),
    path_to_template("aihn_dark__n_comments_levels_0_3_options_off"),
]
