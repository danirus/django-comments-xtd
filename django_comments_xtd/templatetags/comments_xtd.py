# ruff: noqa: RUF100, PLR2004, PLR0913
import copy
import hashlib
import logging

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from django import template
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django_comments.templatetags.comments import (
    BaseCommentNode,
    RenderCommentFormNode,
)

from django_comments_xtd import get_model as get_comment_model
from django_comments_xtd import get_reaction_enum
from django_comments_xtd.conf import settings
from django_comments_xtd.templating import get_template_list
from django_comments_xtd.utils import (
    get_app_model_options,
    get_list_order,
    get_max_thread_level,
)

XtdComment = get_comment_model()

logger = logging.getLogger(__name__)

register = template.Library()


class BaseXtdCommentNode(BaseCommentNode):
    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return (
                ContentType.objects.get_for_model(
                    obj,
                    for_concrete_model=settings.COMMENTS_XTD_FOR_CONCRETE_MODEL,
                ),
                obj.pk,
            )
        else:
            return self.ctype, self.object_pk_expr.resolve(
                context, ignore_failures=True
            )

    def get_queryset(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        mtl = get_max_thread_level(ctype)
        order_by_tuple = get_list_order(ctype)
        return (
            super()
            .get_queryset(context)
            .filter(level__lte=mtl)
            .order_by(*order_by_tuple)
        )


class XtdCommentListNode(BaseXtdCommentNode):
    """Insert a list of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        return qs


class RenderXtdCommentListNode(XtdCommentListNode):
    """Render the comment list directly."""

    def __init__(
        self,
        ctype=None,
        object_pk_expr=None,
        object_expr=None,
        options_enabled=None,
        include_vars=None,
    ):
        super().__init__(
            ctype=ctype,
            object_pk_expr=object_pk_expr,
            object_expr=object_expr,
        )
        self.options_enabled = options_enabled
        self.include_vars = self.parse_include_vars(include_vars)

    def parse_include_vars(self, pairs):
        include_vars = []
        for var_name, var_expr in [pair.split("=") for pair in pairs]:
            include_vars.append((var_name, template.Variable(var_expr)))
        return include_vars

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_xtdcomment_list and return a Node."""
        tokens = token.split_contents()
        force_allow_options = {
            "force_allow_flagging": "comments_flagging_enabled",
            "force_allow_reacting": "comments_reacting_enabled",
            "force_allow_voting": "comments_voting_enabled",
        }
        options_enabled = {}
        tag = tokens.pop(0)
        include_vars = []

        # There must be at least a 'for <object>' or 'for <app.model> <pk>'
        if len(tokens) < 2 or tokens[0] != "for":
            raise template.TemplateSyntaxError(
                f"Template tag {tag!r} must contain either 'for <object>' "
                "or 'for <app.model> <pk>'."
            )

        # Extract 'force_allow_<option>' keys from the red tokens.
        for key, option in force_allow_options.items():
            if key in tokens:
                options_enabled[option] = True
                tokens.pop(tokens.index(key))

        # Extract pairs 'var_name=var_expr'.
        if "with" in tokens:
            t_with_pos = tokens.index("with")
            # From 'with' on, tokens must be pairs vname=vexpr.
            for pair in tokens[t_with_pos + 1 : len(tokens)]:
                if pair.find("=") == -1:
                    raise template.TemplateSyntaxError(
                        f"Expected an assignment expression in {tag!r} "
                        "but found: {pair}."
                    )
                tokens.pop(tokens.index(pair))
                include_vars.append(pair)
            tokens.pop(t_with_pos)  # Remove 'with' token from tokens.

        token = tokens.pop(0)  # This must be the token 'for'.

        if len(tokens) == 1:
            return cls(
                object_expr=parser.compile_filter(tokens[0]),
                options_enabled=options_enabled,
                include_vars=include_vars,
            )

        # {% render_xtdcomment_list for app.models pk %}
        elif len(tokens) == 2:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[0], tag),
                object_pk_expr=parser.compile_filter(tokens[1]),
                options_enabled=options_enabled,
                include_vars=include_vars,
            )

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return ""

        flat_ctx = context.flatten()
        for var_name, var_expr in self.include_vars:
            flat_ctx[var_name] = var_expr.resolve(context)

        highlight_cid = context.request.session.pop("djcx_highlight_cid", None)
        template_search_list = get_template_list(
            "list",
            app_label=ctype.app_label,
            model=ctype.model,
            theme=flat_ctx.get("comments_theme", settings.COMMENTS_XTD_THEME),
        )
        options = get_app_model_options(content_type=ctype)
        check_input_allowed_str = options.pop("check_input_allowed")
        check_func = import_string(check_input_allowed_str)
        target_obj = ctype.get_object_for_this_type(pk=object_pk)
        options["comments_input_allowed"] = check_func(target_obj)

        flat_ctx.update(
            {
                "highlight_cid": highlight_cid,
                "max_thread_level": get_max_thread_level(ctype),
                "comment_list": self.get_context_value_from_queryset(
                    context, self.get_queryset(context)
                ),
                "reply_stack": [],  # List to control comment replies rendering.
            }
        )
        flat_ctx.update(options)
        flat_ctx.update(self.options_enabled)
        liststr = render_to_string(template_search_list, flat_ctx)
        return liststr


@register.tag
def render_xtdcomment_list(parser, token):
    """
    Renders the comment list (as returned by ``{% get_xtdcomment_list %}``)
    through the ``comments/list.html`` templates.

    Syntax::

        {% render_xtdcomment_list for [object] [force_allow_flagging]
           [force_allow_reacting] [force_allow_voting]
           [with vname1=<obj1> ...] %}
        {% render_xtdcomment_list for [app].[model] [obj_id]
           [force_allow_flagging] [force_allow_reacting]
           [force_allow_voting] [with vname1=<obj1> ...] %}

    Special meaning has the variable 'comments_theme'. When pass in the
    'with' part it is used to retrieve the 'list.html' template from the
    given django-comments-xtd theme.

    Examples of usage::

        {% render_xtdcomment_list for story %}
        {% render_xtdcomment_list for story force_allow_voting %}
        {% render_xtdcomment_list for blog.story 1 force_allow_voting %}
        {% render_xtdcomment_list for story
           with comments_theme=avatar_in_thread %}

    """
    return RenderXtdCommentListNode.handle_token(parser, token)


# ---------------------------------------------------------------------
class RenderXtdCommentThreadNode(template.Node):
    def __init__(self, comment, comment_list):
        self.comment = template.Variable(comment)
        self.comment_list = template.Variable(comment_list)

    def render(self, context):
        comment = self.comment.resolve(context)
        comment_list = self.comment_list.resolve(context)
        flat_ctx = context.flatten()
        template_search_list = get_template_list(
            "thread",
            theme=flat_ctx.get("comments_theme", settings.COMMENTS_XTD_THEME),
        )
        nested_comment_list = comment_list.filter(
            parent_id=comment.id, level=comment.level + 1
        )
        flat_ctx.update(
            {
                "comment": comment,
                "nested_comment_list": nested_comment_list,
                "nested_level": comment.level + 1,
            }
        )
        html = render_to_string(template_search_list, flat_ctx)
        return html


@register.tag
def render_xtdcomment_thread(parser, token):
    """
    Renders the given comment and its nested comments in the given queryset.

    Syntax::

        {% render_xtdcomment_thread for [comment] in [comment_list] %}
    """
    tokens = token.contents.split()
    template_syntax_error = (
        "{% render_xtdcomment_thread for <comment> in <comment_list> %}. "
        f"found: {{% {token.contents} %}}."
    )

    if len(tokens) != 5 or tokens[1] != "for" or tokens[3] != "in":
        raise template.TemplateSyntaxError(template_syntax_error)

    return RenderXtdCommentThreadNode(tokens[2], tokens[4])


# ---------------------------------------------------------------------
class XtdCommentCountNode(BaseXtdCommentNode):
    """Insert a count of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        return qs.count()


@register.tag
def get_xtdcomment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the 'as' clause. It differs from {% get_comment_count %} in which it
    caches the result.

    Syntax::

        {% get_xtdcomment_count for [object] as [varname]  %}
        {% get_xtdcomment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_xtdcomment_count for event as comment_count %}
        {% get_xtdcomment_count for calendar.event event.id as comment_count %}
        {% get_xtdcomment_count for calendar.event 17 as comment_count %}

    """
    return XtdCommentCountNode.handle_token(parser, token)


# ---------------------------------------------------------------------
class RenderXtdCommentFormNode(RenderCommentFormNode):
    """
    Almost identical to django_comments' RenderCommentFormNode.

    This class rewrites the `render` method of its parent class, to
    fetch the template from the theme directory.
    """

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = get_template_list(
                "form", app_label=ctype.app_label, model=ctype.model
            )
            context_dict = context.flatten()
            context_dict["form"] = self.get_form(context)
            formstr = render_to_string(template_search_list, context_dict)
            return formstr
        else:
            return ""


@register.tag
def render_xtdcomment_form(parser, token):
    """
    Renders the comments form.

    Syntax::

        {% render_xtdcomment_form for [object] as [varname] %}
        {% render_xtdcomment_form for [app].[model] [object_id] as [varname] %}
    """
    return RenderXtdCommentFormNode.handle_token(parser, token)


class RenderCommentReplyTemplateNode(RenderCommentFormNode):
    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = get_template_list(
                "reply_template", app_label=ctype.app_label, model=ctype.model
            )
            context_dict = context.flatten()
            context_dict["form"] = self.get_form(context)
            formstr = render_to_string(template_search_list, context_dict)
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


class RenderCommentThreads(template.Node):
    def __init__(self, comment, in_reply_box=False):
        self.var_comment = template.Variable(comment)
        self.in_reply_box = in_reply_box

    def get_max_thread_level(self, comment, flat_context):
        max_thread_level = flat_context.get("max_thread_level", None)
        if not max_thread_level:
            ctype = ContentType.objects.get_for_model(
                comment.content_object,
                for_concrete_model=settings.COMMENTS_XTD_FOR_CONCRETE_MODEL,
            )
            max_thread_level = get_max_thread_level(ctype)
        return max_thread_level

    def render(self, context):
        html = ""
        comment = self.var_comment.resolve(context)
        context_dict = context.flatten()
        max_thread_level = self.get_max_thread_level(comment, context_dict)
        if max_thread_level == 0:
            return ""

        reply_stack = context_dict.get("reply_stack")
        for i in range(comment.level + 1):
            if i == max_thread_level and max_thread_level > 0:
                # The last level of comments can't be threaded,
                # therefore they don't display a thread, so no 'anchor'
                # element), however it has to be indented.
                html += '<span class="cthread cthread-end"></span>'
            else:
                if reply_stack[i].id == comment.id:
                    extra = "reply" if self.in_reply_box else "ini"
                    css = f"cthread-l{i} cthread-{extra}"
                else:
                    css = f"cthread-l{i}"
                anchor = (
                    f'<a class="cthread {css}"'
                    f' data-djcx-cthread-id="{reply_stack[i].id}"></a>'
                )
                html += anchor
        return html


class RenderCommentThreadsInReplyBox(RenderCommentThreads):
    def render(self, context):
        html = ""
        comment = self.var_comment.resolve(context)
        context_dict = context.flatten()
        max_thread_level = self.get_max_thread_level(comment, context_dict)
        if max_thread_level == 0:
            return ""

        rs_copy = context_dict.get("reply_stack_copy", None)
        for i in range(len(rs_copy)):
            if rs_copy[i].id == comment.id:
                break
            html += (
                f'<a class="cthread cthread-l{rs_copy[i].level}"'
                f' data-djcx-cthread-id="{rs_copy[i].id}"></a>'
            )

        # Add the the thread corresponding to the comment in the context.
        html += (
            f'<a class="cthread cthread-l{comment.level} cthread-reply"'
            f' data-djcx-cthread-id="{comment.id}"></a>'
        )
        return html


@register.tag
def render_comment_threads(parser, token):
    """
    Render the HTML UI elements that display the thread lines of a comment.
    When the tag contains `in reply_box`, the UI elements provided are
    meant to be used in a reply div, as those rendered by the template
    `comments/reply_button.html`.

    Syntax::

        {% render_comment_threads for <comment> %}
        {% render_comment_threads for <comment> in reply_box %}
    """
    tokens = token.contents.split()

    if tokens[1] != "for":
        raise template.TemplateSyntaxError(
            "Templatetag {tokens[0]!r} syntax is {% render_comment_threads "
            f"for comment %}}. found: {{% {token.contents} %}}."
        )
    if len(tokens) == 5 and tokens[3] == "in" and tokens[4] == "reply_box":
        return RenderCommentThreadsInReplyBox(tokens[2])
    return RenderCommentThreads(tokens[2])


# ----------------------------------------------------------------------
@register.filter
def get_anchor(comment, anchor_pattern=None):
    if anchor_pattern:
        cm_abs_url = comment.get_absolute_url(anchor_pattern)
    else:
        cm_abs_url = comment.get_absolute_url()

    hash_pos = cm_abs_url.find("#")
    return cm_abs_url[hash_pos + 1 :]


# ----------------------------------------------------------------------
@register.simple_tag
def comment_reaction_form_target(comment):
    """
    Get the target URL for the comment reaction form.

    Example::

        <form action="{% comment_reaction_form_target comment %}" method="post">
    """
    return reverse("comments-xtd-react", args=(comment.id,))


@register.simple_tag
def comment_vote_form_target(comment):
    """
    Get the target URL for the comment vote form.

    Example::

        <form action="{% comment_vote_form_target comment %}" method="post">
    """
    return reverse("comments-xtd-vote", args=(comment.id,))


class RenderCommentReactionsButtons(template.Node):
    def __init__(self, user_reactions):
        self.user_reactions = template.Variable(user_reactions)

    def render(self, context):
        context = {
            "reactions": get_reaction_enum(),
            "user_reactions": self.user_reactions.resolve(context),
            "break_every": settings.COMMENTS_XTD_REACTIONS_ROW_LENGTH,
        }
        template_search_list = get_template_list("reactions_buttons")
        htmlstr = render_to_string(template_search_list, context)
        return htmlstr


@register.tag
def render_comment_reactions_buttons(parser, token):
    """
    Renders template with reactions buttons, depending on the selected theme.

    Example usage::

        {% render_comment_reactions_buttons user_reactions %}

    Argument `user_reactions` is a list with `ReactionEnum` items, it
    contains a user's reactions to a comment. The template displays a button
    per each reaction returned from get_comment_reactions_enum().
    Each reaction that is already in the `user_reactions` list is marked as
    already clicked. This templatetag is used within the
    `react_to_comment.html` template.
    """
    try:
        _, args = token.contents.split(None, 1)
    except ValueError as err:
        raise template.TemplateSyntaxError(
            f"{(token.contents.split()[0])!r} tag requires argument"
        ) from err
    user_reactions = args
    return RenderCommentReactionsButtons(user_reactions)


@register.filter
def get_reaction_author_list(cmt_reaction):
    """
    Returns a list with the result of applying the function
    COMMENTS_XTD_FN_USER_REPR to each author of the given CommentReaction.
    """
    return [
        settings.COMMENTS_XTD_FN_USER_REPR(author)
        for author in cmt_reaction.authors.all()
    ]


@register.filter
def get_comment_reaction_enum(cmt_reaction):
    """
    Helper to get the ReactionEnum corresponding to given CommentReaction.
    """
    return get_reaction_enum()(cmt_reaction.reaction)


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
        ctype = ContentType.objects.get_for_model(
            comment.content_object,
            for_concrete_model=settings.COMMENTS_XTD_FOR_CONCRETE_MODEL,
        )
        max_thread_level = get_max_thread_level(ctype)

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
def copy_reply_stack(reply_stack):
    return copy.copy(reply_stack)


@register.filter
def pop_comments_gte(reply_stack, level_lte=0):
    """
    Helper filter used to list comments in the <comments/list.html> template.
    """
    comments_lte = []
    for index in range(len(reply_stack) - 1, -1, -1):
        if reply_stack[index].level < level_lte:
            break
        comments_lte.append(reply_stack.pop(index))
    return comments_lte


@register.filter
def comments_level(comment_list, level=0):
    """
    Return `thread.id` values from the list of comments in `comment_list`.
    """
    return comment_list.filter(level=level)


@register.simple_tag(takes_context=True)
def push_comment(context, comment):
    """
    Helper filter used to list comments in the <comments/list.html> template.
    """
    context["reply_stack"].append(comment)
    return ""


@register.filter
def get_comment(comment_id: str):
    return get_comment_model().objects.get(pk=int(comment_id))


# ----------------------------------------------------------------------
class GetUserReactionsNode(template.Node):
    def __init__(self, comment, varname):
        self.comment = template.Variable(comment)
        self.varname = varname

    def render(self, context):
        comment = self.comment.resolve(context)
        request = context.get("request", None)

        if not request.user.is_authenticated:
            context[self.varname] = ""
            return ""

        qs = comment.reactions.filter(authors__in=[request.user])
        context[self.varname] = [
            item.reaction for item in qs.order_by("reaction")
        ]
        return ""


@register.tag
def get_user_reactions(parser, token):
    """
    Gets logged in user's reactions for the given comment or an empty char
    if there is no user logged in or the user did not vote for the given
    comment.

    Syntax::

        {% get_user_reactions for [object] as [varname] %}

    Example usage::

        {% get_user_reactions for comment as user_reactions %}
    """
    tokens = token.contents.split()

    if tokens[1] != "for" or tokens[3] != "as" or len(tokens) != 5:
        raise template.TemplateSyntaxError(
            "Templatetag {tokens[0]!r} syntax is {% get_user_reactions for "
            f"[comment] as [varname] %}}. found: {{% {token.contents} %}}."
        )
    return GetUserReactionsNode(tokens[2], tokens[4])


# ----------------------------------------------------------------------
class GetUserVoteNode(template.Node):
    def __init__(self, comment, varname):
        self.comment = template.Variable(comment)
        self.varname = varname

    def render(self, context):
        comment = self.comment.resolve(context)
        request = context.get("request", None)

        if not request.user.is_authenticated:
            context[self.varname] = ""
            return ""

        qs = comment.votes.filter(author=request.user)
        if qs.count() == 0:
            context[self.varname] = ""
        elif qs.count() == 1:
            context[self.varname] = qs[0].vote
        else:
            logger.error(
                "More than one CommentVote for comment ID "
                f"{comment.pk} and user {request.user}."
            )
            context[self.varname] = ""
        return ""


@register.tag
def get_user_vote(parser, token):
    """
    Gets logged in user's vote for the given comment or an empty char if there
    is no user logged in or the user did not vote for the given comment.

    Syntax::

        {% get_user_vote for [object] as [varname] %}

    Example usage::

        {% get_user_vote for comment as user_vote %}
    """
    tokens = token.contents.split()

    if tokens[1] != "for" or tokens[3] != "as" or len(tokens) != 5:
        raise template.TemplateSyntaxError(
            "Templatetag {tokens[0]!r} syntax is {% get_user_vote for "
            f"[comment] as [varname] %}}. found: {{% {token} %}}."
        )
    return GetUserVoteNode(tokens[2], tokens[4])


# ----------------------------------------------------------------------
class RenderCommentReactionsPanelTemplate(template.Node):
    def render(self, context):
        enums_details = [
            (enum.value, enum.label, enum.icon) for enum in get_reaction_enum()
        ]
        context = {
            "enums_details": enums_details,
            "break_every": settings.COMMENTS_XTD_REACTIONS_ROW_LENGTH,
        }
        template_list = get_template_list("reactions_panel")
        htmlstr = render_to_string(template_list, context)
        return htmlstr


@register.tag
def render_comment_reactions_panel_template(parser, token):
    return RenderCommentReactionsPanelTemplate()


# ----------------------------------------------------------------------
# Template tag for themes 'avatar_in_thread' and 'avatar_in_header'


@register.simple_tag
def get_email_gravatar(email, config="48,identicon"):
    size, gravatar_type = config.split(",")
    try:
        size_number = int(size)
    except ValueError as exc:
        raise Http404(
            f"The given size is not a number: {repr(size)!r}%s"
        ) from exc

    digest = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
    sparam = urlencode({"s": str(size)})
    url = f"//www.gravatar.com/avatar/{digest}?{sparam}&d={gravatar_type}"

    return mark_safe(
        f'<img src="{url}"'
        f' height="{size_number}"'
        f' width="{size_number}">'
    )


@register.simple_tag
def get_comment_gravatar(comment, config="48,identicon"):
    email = comment.user.email if comment.user else comment.user_email
    return get_email_gravatar(email, config)
