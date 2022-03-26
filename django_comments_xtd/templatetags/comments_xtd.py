import hashlib
import json
import re
from urllib.parse import urlencode

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import InvalidPage, PageNotAnInteger
from django.http import Http404
from django.template import Library, loader, Node, TemplateSyntaxError, Variable
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from django_comments.templatetags.comments import (
    BaseCommentNode,
    RenderCommentFormNode,
    RenderCommentListNode,
)

from django_comments_xtd import get_model, get_reactions_enum, utils
from django_comments_xtd.api import frontend
from django_comments_xtd.conf import settings
from django_comments_xtd.models import max_thread_level_for_content_type
from django_comments_xtd.paginator import CommentsPaginator


register = Library()


if len(settings.COMMENTS_XTD_THEME_DIR) > 0:
    theme_dir = "themes/%s" % settings.COMMENTS_XTD_THEME_DIR
    theme_dir_exists = utils.does_theme_dir_exist(f"comments/{theme_dir}")
else:
    theme_dir = ""
    theme_dir_exists = False


# List of possible paths to the list.html template file.
_list_html_tmpl = []
if theme_dir_exists:
    _list_html_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/list.html",
            "comments/{theme_dir}/{app_label}/list.html",
            "comments/{theme_dir}/list.html",
        ]
    )
_list_html_tmpl.extend(
    [
        "comments/{app_label}/{model}/list.html",
        "comments/{app_label}/list.html",
        "comments/list.html",
    ]
)


# List of possible paths to the form.html template file.
_form_html_tmpl = []
if theme_dir_exists:
    _form_html_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/form.html",
            "comments/{theme_dir}/{app_label}/form.html",
            "comments/{theme_dir}/form.html",
        ]
    )
_form_html_tmpl.extend(
    [
        "comments/{app_label}/{model}/form.html",
        "comments/{app_label}/form.html",
        "comments/form.html",
    ]
)


# List of possible paths to the reply_template.html template file.
_reply_template_html_tmpl = []
if theme_dir_exists:
    _reply_template_html_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/reply_template.html",
            "comments/{theme_dir}/{app_label}/reply_template.html",
            "comments/{theme_dir}/reply_template.html",
        ]
    )
_reply_template_html_tmpl.extend(
    [
        "comments/{app_label}/{model}/reply_template.html",
        "comments/{app_label}/reply_template.html",
        "comments/reply_template.html",
    ]
)


if theme_dir_exists:
    _reactions_panel_template_tmpl = [
        f"comments/{theme_dir}/reactions_panel_template.html",
        "comments/reactions_panel_template.html",
    ]
else:
    _reactions_panel_template_tmpl = "comments/reactions_panel_template.html"


def paginate_queryset(queryset, context):
    """
    Returns dict with pagination data for the given queryset and context.
    """
    request = context.get("request", None)
    num_orphans = settings.COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS
    page_size = settings.COMMENTS_XTD_ITEMS_PER_PAGE
    qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    if page_size == 0:
        return {
            "paginator": None,
            "page_obj": None,
            "is_paginated": False,
            "cpage_qs_param": qs_param,
            "comment_list": queryset,
        }

    paginator = CommentsPaginator(queryset, page_size, orphans=num_orphans)
    page = (request and request.GET.get(qs_param, None)) or 1
    try:
        page_number = int(page)
    except ValueError:
        if page == "last":
            page_number = paginator.num_pages
        else:
            raise Http404(
                _("Page is not “last”, nor can it " "be converted to an int.")
            )
    try:
        page = paginator.page(page_number)
        return {
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": page.has_other_pages(),
            "cpage_qs_param": qs_param,
            "comment_list": page.object_list,
        }
    except InvalidPage as exc:
        raise Http404(
            _("Invalid page (%(page_number)s): %(message)s")
            % {"page_number": page_number, "message": str(exc)}
        )


class RenderXtdCommentListNode(RenderCommentListNode):
    """Render the comment list directly."""

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_xtdcomment_list and return a Node."""
        tokens = token.split_contents()
        if tokens[1] != "for":
            raise TemplateSyntaxError(
                "Second argument in %r tag must be 'for'" % tokens[0]
            )

        # {% render_xtdcomment_list for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_xtdcomment_list for app.model pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
            )

        # {% render_xtdcomment_list for [obj | app.model pk] [using tmpl] %}
        elif len(tokens) > 4 and len(tokens) < 7:
            template_path = tokens[-1]
            num_tokens_between = tokens.index("using") - tokens.index("for")
            if num_tokens_between == 2:
                # {% render_xtdcomment_list for object using tmpl}
                return cls(
                    object_expr=parser.compile_filter(tokens[2]),
                    template_path=template_path,
                )
            elif num_tokens_between == 3:
                # {% render_xtdcomment_list for app.model pk using tmpl}
                tag_t, app_t = tokens[0], tokens[2]
                ctype = BaseCommentNode.lookup_content_type(app_t, tag_t)
                return cls(
                    ctype=ctype,
                    object_pk_expr=parser.compile_filter(tokens[3]),
                    template_path=template_path,
                )
        else:
            msg = (
                "Wrong syntax in %r tag. Valid syntaxes are: "
                "{%% render_xtdcomment_list for [object] [using "
                "<template>] %%} or {%% render_xtdcomment_list for "
                "[app].[model] [obj_id] [using <tmpl>] %%}"
            )
            raise TemplateSyntaxError(msg % tokens[0])

    def __init__(self, *args, **kwargs):
        self.template_path = None
        if "template_path" in kwargs:
            self.template_path = kwargs.pop("template_path")
        super().__init__(*args, **kwargs)

    def render(self, context):
        try:
            ctype, object_pk = self.get_target_ctype_pk(context)
        except AttributeError:
            # in get_target_ctype_pk the call to FilterExpression.resolve does
            # not raise VariableDoesNotExist, however in a latter step an
            # AttributeError is raised when the object_expr does not exist
            # in the context. Therefore, this except raises when used as:
            # {% render_xtdcomment_list for var_not_in_context %}
            return ""
        template_list = [
            pth.format(
                theme_dir=theme_dir,
                app_label=ctype.app_label,
                model=ctype.model,
            )
            for pth in _list_html_tmpl
        ]
        print(template_list)
        qs = self.get_queryset(context)
        qs = self.get_context_value_from_queryset(context, qs)
        context_dict = context.flatten()
        context_dict.update(paginate_queryset(qs, context))

        # Pass max_thread_level in the context.
        app_model = "%s.%s" % (ctype.app_label, ctype.model)
        qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
        MTL = settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL
        mtl = MTL.get(app_model, settings.COMMENTS_XTD_MAX_THREAD_LEVEL)
        context_dict.update(
            {
                "dcx_theme_dir": theme_dir,
                "comments_page_qs_param": qs_param,
                "max_thread_level": mtl,
                "reply_stack": [],  # List to control reply rendering.
            }
        )

        # Pass values for Reactions JS Overlays to the context.
        roverlays = utils.get_reactions_js_overlays(content_type=app_model)
        popover_overlay = roverlays["popover"]
        tooltip_overlay = roverlays["tooltip"]
        context_dict.update(
            {
                "reactions_popover_pos_bottom": popover_overlay["pos_bottom"],
                "reactions_popover_pos_left": popover_overlay["pos_left"],
                "reactions_tooltip_pos_bottom": tooltip_overlay["pos_bottom"],
                "reactions_tooltip_pos_left": tooltip_overlay["pos_left"],
            }
        )

        # get_app_model_options returns a dict like: {
        #     'who_can_post': 'all' | 'users',
        #     'check_input_allowed': 'string path to function',
        #     'comment_flagging_enabled': <boolean>,
        #     'comment_reactions_enabled': <boolean>,
        #     'object_reactions_enabled': <boolean>
        # }
        options = utils.get_app_model_options(content_type=app_model)
        check_input_allowed_str = options.pop("check_input_allowed")
        check_func = import_string(check_input_allowed_str)
        target_obj = ctype.get_object_for_this_type(pk=object_pk)

        # Call the function that checks whether comments input
        # is still allowed on the given target_object. And add
        # the resulting boolean to the template context.
        #
        options["is_input_allowed"] = check_func(target_obj)
        context_dict.update(options)

        liststr = loader.render_to_string(
            self.template_path or template_list, context_dict
        )
        return liststr


@register.tag
def render_xtdcomment_list(parser, token):
    """
    Render the comment list (as returned by ``{% get_xtdcomment_list %}``)
    through the ``comments/list.html`` templates.

    Syntax::

        {% render_xtdcomment_list for [object] [...] %}
        {% render_xtdcomment_list for [app].[model] [obj_id] [...] %}
        {% render_xtdcomment_list for ... [using <tmpl>] %}

    Example usage::

        {% render_xtdcomment_list for post %}

    """
    return RenderXtdCommentListNode.handle_token(parser, token)


class RenderXtdCommentFormNode(RenderCommentFormNode):
    """
    Almost identical to django_comments' RenderCommentFormNode.

    This class rewrites the `render` method of its parent class, to
    fetch the template from the theme directory.
    """

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_list = [
                pth.format(
                    theme_dir=theme_dir,
                    app_label=ctype.app_label,
                    model=ctype.model,
                )
                for pth in _form_html_tmpl
            ]
            context_dict = context.flatten()
            context_dict["form"] = self.get_form(context)
            formstr = loader.render_to_string(template_list, context_dict)
            return formstr
        else:
            return ""


@register.tag
def render_xtdcomment_form(parser, token):
    """
    Render "comments/<theme_dir>/form.html" or "comments/form.html".

    Syntax::

        {% get_xtdcomment_form for [object] as [varname] %}
        {% get_xtdcomment_form for [app].[model] [object_id] as [varname] %}
    """
    return RenderXtdCommentFormNode.handle_token(parser, token)


class RenderCommentReplyTemplateNode(RenderCommentFormNode):
    def render(self, context):
        qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_list = [
                pth.format(
                    theme_dir=theme_dir,
                    app_label=ctype.app_label,
                    model=ctype.model,
                )
                for pth in _reply_template_html_tmpl
            ]
            context_dict = context.flatten()
            context_dict.update(
                {
                    "form": self.get_form(context),
                    "comments_page_qs_param": qs_param,
                    "dcx_theme_dir": theme_dir,
                }
            )
            formstr = loader.render_to_string(template_list, context_dict)
            return formstr
        else:
            return ""


@register.tag
def render_comment_reply_template(parser, token):
    """
    Render the comment reply form to be used by the JavaScript plugin.

    Syntax::

        {% render_comment_reply_template for [object] %}
        {% render_comment_reply_template for [app].[model] [object_id] %}
    """
    return RenderCommentReplyTemplateNode.handle_token(parser, token)


@register.simple_tag()
def get_xtdcomment_permalink(comment, page_number=None, anchor_pattern=None):
    """
    Get the permalink for a comment, optionally specifying the format of the
    named anchor to be appended to the end of the URL.

    Example::
        {% get_xtdcomment_permalink comment page_obj.number "#c%(id)s" %}
    """
    try:
        if anchor_pattern:
            cm_abs_url = comment.get_absolute_url(anchor_pattern)
        else:
            cm_abs_url = comment.get_absolute_url()

        hash_pos = cm_abs_url.find("#")
        cm_anchor = cm_abs_url[hash_pos:]
        cm_abs_url = cm_abs_url[:hash_pos]
    except Exception:
        return comment.get_absolute_url()

    if not page_number:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_("That page number is not an integer"))

    if page_number > 1:
        qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
        return f"{cm_abs_url}?{qs_param}={page_number}{cm_anchor}"
    else:
        return f"{cm_abs_url}{cm_anchor}"


# ----------------------------------------------------------------------
class GetCommentsAPIPropsNode(Node):
    def __init__(self, obj):
        self.obj = Variable(obj)

    def render(self, context):
        obj = self.obj.resolve(context)
        user = context.get("user", None)
        request = context.get("request", None)
        props = frontend.comments_api_props(obj, user, request=request)
        return json.dumps(props)


@register.tag
def get_comments_api_props(parser, token):
    """
    Returns a JSON with properties required to use the REST API.

    See api.frontend.comments_props for full details on the props.

    Example::
        {% get_comments_api_props for comment %}
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0]
        )
    match = re.search(r"for (\w+)", args)
    if not match:
        raise TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    obj = match.groups()[0]
    return GetCommentsAPIPropsNode(obj)


# ----------------------------------------------------------------------
@register.simple_tag
def comment_reaction_form_target(comment):
    """
    Get the target URL for the comment reaction form.

    Example::

        <form action="{% comment_reaction_form_target comment %}" method="post">
    """
    return reverse("comments-xtd-react", args=(comment.id,))


@register.inclusion_tag(f"comments/{theme_dir}/reactions_buttons.html")
def render_reactions_buttons(user_reactions):
    """
    Renders template `comments/reactions_buttons.html`.

    Argument `user_reactions` is a list with `ReactionEnum` items, it
    contains a user's reactions to a comment. The template display a button
    per each reaction returned from get_reactions_enum(). Each reaction that
    is already in the `user_reactions` list is marked as already clicked.
    This templatetag is used within the `react.html` template.
    """
    return {
        "reactions": get_reactions_enum(),
        "user_reactions": user_reactions,
        "break_every": settings.COMMENTS_XTD_REACTIONS_ROW_LENGTH,
    }


@register.filter
def authors_list(cmt_reaction):
    """
    Returns a list with the result of applying the function
    COMMENTS_XTD_API_USER_REPR to each authour of the given CommentReaction.
    """
    return [
        settings.COMMENTS_XTD_API_USER_REPR(author)
        for author in cmt_reaction.authors.all()
    ]


@register.filter
def get_reaction_enum(cmt_reaction):
    """
    Helper to get the ReactionEnum corresponding to given CommentReaction.
    """
    return get_reactions_enum()(cmt_reaction.reaction)


# ----------------------------------------------------------------------
@register.simple_tag(takes_context=True)
def comment_css_thread_range(context, comment, prefix="l"):
    """
    Helper tag to return a string of CSS selectors that render vertical
    lines to represent comment threads. When comment's level matches the
    max_thread_level there is no vertical line as comments in the
    max_thread_level can not receivereplies.

    Returns a concatenated string of f'{prefix}{i}' for i in range(level + 1).
    When the given comment has level=2, and the maximum thread level is 2:

        `{% comment_css_thread_range comment %}`

    produces the string: "l0-mid l1-mid l2".
    """
    max_thread_level = context.get("max_thread_level", None)
    if not max_thread_level:
        ctype = ContentType.objects.get_for_model(comment.content_object)
        max_thread_level = max_thread_level_for_content_type(ctype)

    result = ""
    for i in range(comment.level + 1):
        if i == comment.level:
            if comment.level == max_thread_level:
                result += f"{prefix}{i} "
            else:
                result += f"{prefix}{i}-ini "
        else:
            result += f"{prefix}{i}-mid "
    return result.rstrip()


@register.filter(is_safe=True)
def reply_css_thread_range(level, prefix="l"):
    """
    Helper filter to return a string of CSS selectors that render vertical
    lines to represent comment threads. When comment level matches the
    max_thread_level there is no vertical line, as comments in the
    max_thread_level can not receive replies.

    Returns a concatenated string of f'{prefix}{i}' for i in range(level + 1).
    If the given comment object has level=1, using the filter as:

        `{{ comment.level|reply_css_thread_range }}`

    produces the string: "l0 l1".
    """
    result = ""
    for i in range(level + 1):
        result += f"{prefix}{i} "
    return mark_safe(result.rstrip())


@register.filter(is_safe=True)
def indent_divs(level, prefix="level-"):
    """
    Helper filter to return a concatenated string of divs for indentation.

    When called as {{ 2|indent_divs }} produces the string:

        '<div class="level-1"></div>
         <div class="level-2"></div>'
    """
    result = ""
    for i in range(1, level + 1):
        result += f'<div class="{prefix}{i}"></div>'
    return mark_safe(result)


@register.filter(is_safe=True)
def hline_div(level, prefix="line-"):
    """
    Helper filter to eeturns a DIV that renders a horizontal line connecting
    the vertical comment thread line with the comment reply box.

    When called as {{ comment.level|hline_div }} produces the string:

        '<div class="line-{comment.level}"></div>'
    """
    return mark_safe(f'<div class="{prefix}{level}"></div>')


@register.filter
def get_top_comment(reply_stack):
    """
    Helper filter used to list comments in the <comments/list.html> template.
    """
    return reply_stack[-1]


@register.filter
def pop_comments_gte(reply_stack, level_lte=0):
    """
    Helper filter used to list comments in the <comments/list.html> template.
    """
    comments_lte = []
    try:
        for index in range(len(reply_stack) - 1, -1, -1):
            if reply_stack[index].level < level_lte:
                break
            comments_lte.append(reply_stack.pop(index))
    finally:
        return comments_lte


@register.simple_tag(takes_context=True)
def push_comment(context, comment):
    """
    Helper filter used to list comments in the <comments/list.html> template.
    """
    context["reply_stack"].append(comment)
    return ""


@register.filter
def get_comment(comment_id: str):
    return get_model().objects.get(pk=int(comment_id))


@register.simple_tag()
def dcx_custom_selector():
    return f"{settings.COMMENTS_XTD_CSS_CUSTOM_SELECTOR}"


@register.simple_tag()
def get_dcx_theme_dir():
    return theme_dir


# ----------------------------------------------------------------------
@register.inclusion_tag("comments/only_users_can_post.html")
def render_only_users_can_post_template(object):
    return {"html_id_suffix": utils.get_html_id_suffix(object)}


@register.inclusion_tag(_reactions_panel_template_tmpl)
def render_reactions_panel_template():
    enums_details = [
        (enum.value, enum.label, enum.icon) for enum in get_reactions_enum()
    ]
    return {
        "enums_details": enums_details,
        "break_every": settings.COMMENTS_XTD_REACTIONS_ROW_LENGTH,
    }


# ----------------------------------------------------------------------
# Template tag for themes 'avatar_in_thread' and 'avatar_in_header'


def get_gravatar_url(email, size=48, avatar="identicon"):
    """
    This is the parameter of the production avatar.
    The first parameter is the way of generating the
    avatar and the second one is the size.
    The way os generating has mp/identicon/monsterid/wavatar/retro/hide.
    """
    return "//www.gravatar.com/avatar/%s?%s&d=%s" % (
        hashlib.md5(email.lower().encode("utf-8")).hexdigest(),
        urlencode({"s": str(size)}),
        avatar,
    )


if apps.is_installed("avatar"):

    from avatar.templatetags.avatar_tags import avatar
    from avatar.utils import cache_result

    @cache_result
    @register.simple_tag
    def get_user_avatar_or_gravatar(email, config="48,identicon"):
        size, gravatar_type = config.split(",")
        try:
            size_number = int(size)
        except ValueError:
            raise Http404(_("The given size is not a number: %s" % repr(size)))

        try:
            user = get_user_model().objects.get(email=email)
            return avatar(user, size_number)
        except get_user_model().DoesNotExist:
            url = get_gravatar_url(email, size_number, gravatar_type)
            return mark_safe(
                '<img src="%s" height="%d" width="%d">'
                % (url, size_number, size_number)
            )
