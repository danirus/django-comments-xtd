from django.utils.module_loading import import_string

from django_comments_xtd.conf import settings

template_patterns = {
    "bad_form": {
        "themed": [
            "comments/{theme_dir}/bad_form.html",
            "comments/bad_form.html",
        ],
        "default": [
            "comments/bad_form.html",
        ],
    },
    "discarded": {
        "themed": [
            "comments/{theme_dir}/discarded.html",
            "comments/discarded.html",
        ],
        "default": ["comments/discarded.html"],
    },
    "flag": {
        "themed": [
            "comments/{theme_dir}/flag.html",
            "comments/flag.html",
        ],
        "default": [
            "comments/flag.html",
        ],
    },
    "flag_js": {
        "themed": [
            "comments/{theme_dir}/comment_flags.html",
            "comments/comment_flags.html",
        ],
        "default": [
            "comments/comment_flags.html",
        ],
    },
    "form": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/form.html",
            "comments/{theme_dir}/{app_label}/form.html",
            "comments/{theme_dir}/form.html",
            "comments/{app_label}/{model}/form.html",
            "comments/{app_label}/form.html",
            "comments/form.html",
        ],
        "default": [
            "comments/{app_label}/{model}/form.html",
            "comments/{app_label}/form.html",
            "comments/form.html",
        ],
    },
    "form_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/form_js.html",
            "comments/{theme_dir}/{app_label}/form_js.html",
            "comments/{theme_dir}/form_js.html",
            "comments/{app_label}/{model}/form_js.html",
            "comments/{app_label}/form_js.html",
            "comments/form_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/form_js.html",
            "comments/{app_label}/form_js.html",
            "comments/form_js.html",
        ],
    },
    "list": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/list.html",
            "comments/{theme_dir}/{app_label}/list.html",
            "comments/{theme_dir}/list.html",
            "comments/{app_label}/{model}/list.html",
            "comments/{app_label}/list.html",
            "comments/list.html",
        ],
        "default": [
            "comments/{app_label}/{model}/list.html",
            "comments/{app_label}/list.html",
            "comments/list.html",
        ],
    },
    "moderated": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/moderated.html",
            "comments/{theme_dir}/{app_label}/moderated.html",
            "comments/{theme_dir}/moderated.html",
            "comments/{app_label}/{model}/moderated.html",
            "comments/{app_label}/moderated.html",
            "comments/moderated.html",
        ],
        "default": [
            "comments/{app_label}/{model}/moderated.html",
            "comments/{app_label}/moderated.html",
            "comments/moderated.html",
        ],
    },
    "moderated_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/moderated_js.html",
            "comments/{theme_dir}/{app_label}/moderated_js.html",
            "comments/{theme_dir}/moderated_js.html",
            "comments/{app_label}/{model}/moderated_js.html",
            "comments/{app_label}/moderated_js.html",
            "comments/moderated_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/moderated_js.html",
            "comments/{app_label}/moderated_js.html",
            "comments/moderated_js.html",
        ],
    },
    "muted": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/muted.html",
            "comments/{theme_dir}/{app_label}/muted.html",
            "comments/{theme_dir}/muted.html",
            "comments/{app_label}/{model}/muted.html",
            "comments/{app_label}/muted.html",
            "comments/muted.html",
        ],
        "default": [
            "comments/{app_label}/{model}/muted.html",
            "comments/{app_label}/muted.html",
            "comments/muted.html",
        ],
    },
    "posted": {
        "themed": ["comments/{theme_dir}/posted.html", "comments/posted.html"],
        "default": ["comments/posted.html"],
    },
    "posted_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/posted_js.html",
            "comments/{theme_dir}/{app_label}/posted_js.html",
            "comments/{theme_dir}/posted_js.html",
            "comments/{app_label}/{model}/posted_js.html",
            "comments/{app_label}/posted_js.html",
            "comments/posted_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/posted_js.html",
            "comments/{app_label}/posted_js.html",
            "comments/posted_js.html",
        ],
    },
    "preview": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/preview.html",
            "comments/{theme_dir}/{app_label}/preview.html",
            "comments/{theme_dir}/preview.html",
            "comments/{app_label}/{model}/preview.html",
            "comments/{app_label}/preview.html",
            "comments/preview.html",
        ],
        "default": [
            "comments/{app_label}/{model}/preview.html",
            "comments/{app_label}/preview.html",
            "comments/preview.html",
        ],
    },
    "published_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/published_js.html",
            "comments/{theme_dir}/{app_label}/published_js.html",
            "comments/{theme_dir}/published_js.html",
            "comments/{app_label}/{model}/published_js.html",
            "comments/{app_label}/published_js.html",
            "comments/published_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/published_js.html",
            "comments/{app_label}/published_js.html",
            "comments/published_js.html",
        ],
    },
    "react": {
        "themed": [
            "comments/{theme_dir}/react.html",
            "comments/react.html",
        ],
        "default": ["comments/react.html"],
    },
    "reacted": {
        "themed": [
            "comments/{theme_dir}/reacted.html",
            "comments/reacted.html",
        ],
        "default": ["comments/reacted.html"],
    },
    "reacted_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/"
            "comment_reactions_js.html",
            "comments/{theme_dir}/{app_label}/comment_reactions_js.html",
            "comments/{theme_dir}/comment_reactions_js.html",
            "comments/{app_label}/{model}/comment_reactions_js.html",
            "comments/{app_label}/comment_reactions_js.html",
            "comments/comment_reactions_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/comment_reactions_js.html",
            "comments/{app_label}/comment_reactions_js.html",
            "comments/comment_reactions_js.html",
        ],
    },
    "reactions_buttons": {
        "themed": [
            "comments/{theme_dir}/reactions_buttons.html",
            "comments/reactions_buttons.html",
        ],
        "default": ["comments/reactions_buttons.html"],
    },
    "reactions_panel": {
        "themed": [
            "comments/{theme_dir}/reactions_panel_template.html",
            "comments/reactions_panel_template.html",
        ],
        "default": ["comments/reactions_panel_template.html"],
    },
    "reply": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/reply.html",
            "comments/{theme_dir}/{app_label}/reply.html",
            "comments/{theme_dir}/reply.html",
            "comments/{app_label}/{model}/reply.html",
            "comments/{app_label}/reply.html",
            "comments/reply.html",
        ],
        "default": [
            "comments/{app_label}/{model}/reply.html",
            "comments/{app_label}/reply.html",
            "comments/reply.html",
        ],
    },
    "reply_form_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/reply_form_js.html",
            "comments/{theme_dir}/{app_label}/reply_form_js.html",
            "comments/{theme_dir}/reply_form_js.html",
            "comments/{app_label}/{model}/reply_form_js.html",
            "comments/{app_label}/reply_form_js.html",
            "comments/reply_form_js.html",
        ],
        "default": [
            "comments/{app_label}/{model}/reply_form_js.html",
            "comments/{app_label}/reply_form_js.html",
            "comments/reply_form_js.html",
        ],
    },
    "reply_template": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/reply_template.html",
            "comments/{theme_dir}/{app_label}/reply_template.html",
            "comments/{theme_dir}/reply_template.html",
            "comments/{app_label}/{model}/reply_template.html",
            "comments/{app_label}/reply_template.html",
            "comments/reply_template.html",
        ],
        "default": [
            "comments/{app_label}/{model}/reply_template.html",
            "comments/{app_label}/reply_template.html",
            "comments/reply_template.html",
        ],
    },
    "thread": {
        "themed": [
            "comments/{theme_dir}/thread.html",
            "comments/thread.html",
        ],
        "default": [
            "comments/thread.html",
        ],
    },
    "users_reacted_to_comment": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/"
            "users_reacted_to_comment.html",
            "comments/{theme_dir}/{app_label}/users_reacted_to_comment.html",
            "comments/{theme_dir}/users_reacted_to_comment.html",
            "comments/{app_label}/{model}/users_reacted_to_comment.html",
            "comments/{app_label}/users_reacted_to_comment.html",
            "comments/users_reacted_to_comment.html",
        ],
        "default": [
            "comments/{app_label}/{model}/users_reacted_to_comment.html",
            "comments/{app_label}/users_reacted_to_comment.html",
            "comments/users_reacted_to_comment.html",
        ],
    },
    "vote": {
        "themed": [
            "comments/{theme_dir}/vote.html",
            "comments/vote.html",
        ],
        "default": ["comments/vote.html"],
    },
    "voted": {
        "themed": [
            "comments/{theme_dir}/voted.html",
            "comments/voted.html",
        ],
        "default": ["comments/voted.html"],
    },
    "voted_js": {
        "themed": [
            "comments/{theme_dir}/{app_label}/{model}/comment_votes.html",
            "comments/{theme_dir}/{app_label}/comment_votes.html",
            "comments/{theme_dir}/comment_votes.html",
            "comments/{app_label}/{model}/comment_votes.html",
            "comments/{app_label}/comment_votes.html",
            "comments/comment_votes.html",
        ],
        "default": [
            "comments/{app_label}/{model}/comment_votes.html",
            "comments/{app_label}/comment_votes.html",
            "comments/comment_votes.html",
        ],
    },
}

_template_patterns = import_string(settings.COMMENTS_XTD_TEMPLATE_PATTERNS)


def get_template_list(template_alias: str, **kwargs) -> list[str]:
    theme = kwargs.get("theme", settings.COMMENTS_XTD_THEME)
    subkey = "themed" if len(theme) else "default"
    template_list = _template_patterns[template_alias][subkey]
    return [
        t.format(theme_dir=f"themes/{theme}", **kwargs) for t in template_list
    ]
