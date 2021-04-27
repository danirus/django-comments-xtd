import json
import hashlib
import re

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.contrib.contenttypes.models import ContentType
from django.template import (Library, Node, TemplateSyntaxError,
                             Variable, loader)
from django.urls import reverse
from django.utils.safestring import mark_safe


from django_comments.templatetags import comments

from django_comments_xtd import (get_model as get_comment_model,
                                 get_reactions_enum)
from django_comments_xtd.api import frontend
from django_comments_xtd.conf import settings
from django_comments_xtd.models import max_thread_level_for_content_type
from django_comments_xtd.utils import (get_app_model_options,
                                       get_current_site_id, get_html_id_suffix)


register = Library()


# ----------------------------------------------------------------------
class XtdCommentCountNode(Node):
    """Store the number of XtdComments for the given list of app.models"""

    def __init__(self, as_varname, content_types):
        """Class method to parse get_xtdcomment_list and return a Node."""
        self.as_varname = as_varname
        self.qs = get_comment_model().objects.for_content_types(content_types)
        self.qs = self.qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True):
            self.qs = self.qs.filter(is_removed=False)

    def render(self, context):
        site_id = getattr(settings, "SITE_ID", None)
        if not site_id and ('request' in context):
            site_id = get_current_site_id(context['request'])
        context[self.as_varname] = self.qs.filter(site=site_id).count()
        return ''


@register.tag
def get_xtdcomment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_xtdcomment_count as var for app.model [app.model] %}

    Example usage::

        {% get_xtdcomment_count as comments_count for blog.story blog.quote %}

    """
    tokens = token.contents.split()

    if tokens[1] != 'as':
        raise TemplateSyntaxError("2nd. argument in %r tag must be 'for'" %
                                  tokens[0])

    as_varname = tokens[2]

    if tokens[3] != 'for':
        raise TemplateSyntaxError("4th. argument in %r tag must be 'for'" %
                                  tokens[0])

    content_types = _get_content_types(tokens[0], tokens[4:])
    return XtdCommentCountNode(as_varname, content_types)


# ----------------------------------------------------------------------
class WhoCanPostNode(Node):
    """Stores the who_can_post value from COMMENTS_XTD_APP_MODEL_OPTION"""

    def __init__(self, content_type, as_varname):
        self.content_type = content_type
        self.as_varname = as_varname

    def render(self, context):
        context[self.as_varname] = get_app_model_options(
            content_type=self.content_type)['who_can_post']
        return ''


@register.tag
def get_who_can_post(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_who_can_post for app.model as var %}

    Example usage::

        {% get_who_can_post for articles.article as who_can_post %}

    """
    tokens = token.contents.split()

    if tokens[1] != 'for':
        raise TemplateSyntaxError("2nd. argument in %r tag must be 'for'" %
                                  tokens[0])

    if tokens[3] != 'as':
        raise TemplateSyntaxError("4th. argument in %r tag must be 'as'" %
                                  tokens[0])

    content_type = _get_content_types(tokens[0], [tokens[2]])
    as_varname = tokens[4]
    return WhoCanPostNode(content_type, as_varname)


# ----------------------------------------------------------------------
class BaseLastXtdCommentsNode(Node):
    """Base class to deal with the last N XtdComments for a list of app.model"""

    def __init__(self, count, content_types, template_path=None):
        """Class method to parse get_xtdcomment_list and return a Node."""
        try:
            self.count = int(count)
        except Exception:
            self.count = Variable(count)

        self.content_types = content_types
        self.template_path = template_path


class RenderLastXtdCommentsNode(BaseLastXtdCommentsNode):
    def render(self, context):
        if not isinstance(self.count, int):
            self.count = int(self.count.resolve(context))

        site_id = getattr(settings, "SITE_ID", None)
        if not site_id and ('request' in context):
            site_id = get_current_site_id(context['request'])

        qs = get_comment_model().objects.for_content_types(
            self.content_types, site=site_id)

        qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True):
            qs = qs.filter(is_removed=False)

        qs = qs.order_by('submit_date')[:self.count]

        strlist = []
        context_dict = context.flatten()
        for xtd_comment in qs:
            if self.template_path:
                template_arg = self.template_path
            else:
                template_arg = [
                    "django_comments_xtd/%s/%s/comment.html" % (
                        xtd_comment.content_type.app_label,
                        xtd_comment.content_type.model),
                    "django_comments_xtd/%s/comment.html" % (
                        xtd_comment.content_type.app_label,),
                    "django_comments_xtd/comment.html"
                ]
            context_dict['comment'] = xtd_comment
            strlist.append(loader.render_to_string(template_arg, context_dict))
        return ''.join(strlist)


class GetLastXtdCommentsNode(BaseLastXtdCommentsNode):
    def __init__(self, count, as_varname, content_types):
        super(GetLastXtdCommentsNode, self).__init__(count, content_types)
        self.as_varname = as_varname

    def render(self, context):
        if not isinstance(self.count, int):
            self.count = int(self.count.resolve(context))

        site_id = getattr(settings, "SITE_ID", None)
        if not site_id and ('request' in context):
            site_id = get_current_site_id(context['request'])

        qs = get_comment_model().objects.for_content_types(
                self.content_types, site=site_id)

        qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True):
            qs = qs.filter(is_removed=False)

        qs = qs.order_by('submit_date')[:self.count]

        context[self.as_varname] = qs
        return ''


def _get_content_types(tagname, tokens):
    content_types = []
    for token in tokens:
        try:
            app, model = token.split('.')
            content_types.append(
                ContentType.objects.get(app_label=app, model=model))
        except ValueError:
            raise TemplateSyntaxError(
                "Argument %s in %r must be in the format 'app.model'" % (
                    token, tagname))
        except ContentType.DoesNotExist:
            raise TemplateSyntaxError(
                "ContentType '%s.%s' used for tag %r doesn't exist" % (
                    app, model, tagname))
    return content_types


@register.tag
def render_last_xtdcomments(parser, token):
    """
    Render the last N XtdComments through the
      ``django_comments_xtd/comment.html`` template

    Syntax::

        {% render_last_xtdcomments N for app.model [app.model] using template %}

    Example usage::

        {% render_last_xtdcomments 5 for blog.story blog.quote using "t.html" %}
    """
    tokens = token.contents.split()
    try:
        count = tokens[1]
    except ValueError:
        raise TemplateSyntaxError(
            "Second argument in %r tag must be a integer" % tokens[0])

    if tokens[2] != 'for':
        raise TemplateSyntaxError(
            "Third argument in %r tag must be 'for'" % tokens[0])

    try:
        token_using = tokens.index("using")
        content_types = _get_content_types(tokens[0], tokens[3:token_using])
        try:
            template = tokens[token_using + 1].strip('" ')
        except IndexError:
            raise TemplateSyntaxError("Last argument in %r tag must be a "
                                      "relative template path" % tokens[0])
    except ValueError:
        content_types = _get_content_types(tokens[0], tokens[3:])
        template = None

    return RenderLastXtdCommentsNode(count, content_types, template)


@register.tag
def get_last_xtdcomments(parser, token):
    """
    Get the last N XtdComments.

    Syntax::

        {% get_last_xtdcomments N as var for app.model [app.model] %}

    Example usage::

        {% get_last_xtdcomments 5 as last_comments for blog.story blog.quote %}

    """
    tokens = token.contents.split()

    try:
        count = int(tokens[1])
    except ValueError:
        raise TemplateSyntaxError(
            "Second argument in %r tag must be a integer" % tokens[0])

    if tokens[2] != 'as':
        raise TemplateSyntaxError(
            "Third argument in %r tag must be 'as'" % tokens[0])

    as_varname = tokens[3]

    if tokens[4] != 'for':
        raise TemplateSyntaxError(
            "Fifth argument in %r tag must be 'for'" % tokens[0])

    content_types = _get_content_types(tokens[0], tokens[5:])
    return GetLastXtdCommentsNode(count, as_varname, content_types)


# ----------------------------------------------------------------------
class RenderXtdCommentListNode(comments.RenderCommentListNode):
    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/list.html" % (ctype.app_label, ctype.model),
                "comments/%s/list.html" % ctype.app_label,
                "comments/list.html"
            ]
            qs = self.get_queryset(context)
            comment_list = self.get_context_value_from_queryset(context, qs)
            context_dict = context.flatten()
            context_dict['comment_list'] = comment_list

            # Pass max_thread_level in the context.
            app_model = "%s.%s" % (ctype.app_label, ctype.model)
            MTL = settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL
            mtl = MTL.get(app_model, settings.COMMENTS_XTD_MAX_THREAD_LEVEL)
            context_dict.update({
                'max_thread_level': mtl,
                'reply_stack': [],  # List to control reply rendering.
                'show_nested': True
            })

            # get_app_model_options returns a dict like: {
            #     'who_can_post': 'all' | 'users',
            #     'allow_comment_flagging': <boolean>,
            #     'allow_comment_reactions': <boolean>,
            #     'allow_object_reactions': <boolean>
            # }
            context_dict.update(
                get_app_model_options(content_type=ctype.app_label)
            )
            liststr = loader.render_to_string(template_search_list,
                                              context_dict)
            return liststr
        else:
            return ''


@register.tag
def render_xtdcomment_list(parser, token):
    """
    Render the comment list (as returned by ``{% get_xtdcomment_list %}``)
    through the ``comments/list.html`` template.

    Syntax::

        {% render_xtdcomment_list for [object] %}
        {% render_xtdcomment_list for [app].[model] [object_id] %}

    Example usage::

        {% render_xtdcomment_list for post %}

    """
    return RenderXtdCommentListNode.handle_token(parser, token)


# ----------------------------------------------------------------------
class GetCommentBoxPropsNode(Node):
    def __init__(self, obj):
        self.obj = Variable(obj)

    def render(self, context):
        obj = self.obj.resolve(context)
        user = context.get('user', None)
        request = context.get('request', None)
        props = frontend.commentbox_props(obj, user, request=request)
        return json.dumps(props)


@register.tag
def get_commentbox_props(parser, token):
    """
    Returns a JSON object with the initial props for the CommentBox component.

    See api.frontend.commentbox_props for full details on the props.
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("%s tag requires arguments" %
                                  token.contents.split()[0])
    match = re.search(r'for (\w+)', args)
    if not match:
        raise TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    obj = match.groups()[0]
    return GetCommentBoxPropsNode(obj)


# ----------------------------------------------------------------------
@register.simple_tag
def comment_reaction_form_target(comment):
    """
    Get the target URL for the comment reaction form.

    Example::

        <form action="{% comment_reaction_form_target comment %}" method="post">
    """
    return reverse("comments-xtd-react", args=(comment.id,))


@register.inclusion_tag('includes/django_comments_xtd/reactions_buttons.html')
def render_reactions_buttons(user_reactions):
    return {
        'reactions': get_reactions_enum(),
        'user_reactions': user_reactions,
        'break_every': settings.COMMENTS_XTD_REACTIONS_ROW_LENGTH
    }


@register.simple_tag
def reactions_enum_strlist():
    """
    Returns a string representing the list of available comment reactions.

    Each reaction is a comma-separated list of 3 items: the ID of the
    reaction, the name, and the HTML code to represent it as a button.
    By default there are 4 reactions represented by emoji characters. Read
    the docs to know how to extend comment reactions.
    """
    return get_reactions_enum().strlist()


@register.filter
def authors_list(cmt_reaction):
    return [settings.COMMENTS_XTD_API_USER_REPR(author)
            for author in cmt_reaction.authors.all()]


@register.filter
def get_reaction_enum(cmt_reaction):
    """Returns the ReactionEnum corresponding to the given CommentReaction."""
    return get_reactions_enum()(cmt_reaction.reaction)


# ----------------------------------------------------------------------
@register.filter
def xtd_comment_gravatar_url(email, size=48, avatar='identicon'):
    """
    This is the parameter of the production avatar.
    The first parameter is the way of generating the
    avatar and the second one is the size.
    The way os generating has mp/identicon/monsterid/wavatar/retro/hide.
    """
    return ("//www.gravatar.com/avatar/%s?%s&d=%s" %
            (hashlib.md5(email.lower().encode('utf-8')).hexdigest(),
             urlencode({'s': str(size)}), avatar))


# ----------------------------------------------------------------------
@register.filter
def xtd_comment_gravatar(email, config='48,identicon'):
    size, avatar = config.split(',')
    url = xtd_comment_gravatar_url(email, size, avatar)
    return mark_safe('<img src="%s" height="%s" width="%s">' %
                     (url, size, size))


# ----------------------------------------------------------------------
@register.filter
def comments_xtd_api_list_url(obj):
    ctype = ContentType.objects.get_for_model(obj)
    ctype_slug = "%s-%s" % (ctype.app_label, ctype.model)
    return reverse('comments-xtd-api-list', kwargs={'content_type': ctype_slug,
                                                    'object_pk': obj.id})


# ----------------------------------------------------------------------
@register.filter
def has_permission(user_obj, str_permission):
    try:
        return user_obj.has_perm(str_permission)
    except Exception as exc:
        raise exc


# ----------------------------------------------------------------------
@register.filter
def can_receive_comments_from(obj, user):
    ct = ContentType.objects.get_for_model(obj)
    app_label = '%s.%s' % (ct.app_label, ct.model)
    options = get_app_model_options(content_type=app_label)
    who_can_post = options['who_can_post']
    if (
            who_can_post == 'all' or
            (who_can_post == 'users' and user.is_authenticated)
    ):
        return True
    else:
        return False


# ----------------------------------------------------------------------
@register.simple_tag(takes_context=True)
def comment_css_thread_range(context, comment, prefix="l"):
    """
    Returns a string of CSS selectors that render vertical lines to represent
    comment threads. When comment level matches the max_thread_level there is
    no vertical line, as comments in the max_thread_level can not receive
    replies.

    Returns a concatenated string of f'{prefix}{i}' for i in range(level + 1).
    When the given comment has level=2, and the maximum thread level is 2:

        `{% comment_css_thread_range comment %}`

    produces the string: "l0-mid l1-mid l2".
    """
    max_thread_level = context.get('max_thread_level', None)
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
    Returns a string of CSS selectors that render vertical lines to represent
    comment threads. When comment level matches the max_thread_level there is
    no vertical line, as comments in the max_thread_level can not receive
    replies.

    Returns a concatenated string of f'{prefix}{i}' for i in range(level + 1).
    If the given comment object has level=1, using the filter as:

        `{{ comment.level|comment_reply_css_thread_range }}`

    produces the string: "l0 l1".
    """
    result = ""
    for i in range(level + 1):
        result += f"{prefix}{i} "
    return mark_safe(result.rstrip())


@register.filter(is_safe=True)
def indent_divs(level, prefix="level-"):
    """
    Returns a concatenated string of "<div class="{prefix}{i}"></div>"
    for i in range(1, level + 1).

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
    Returns a DIV that renders a horizontal line connecting the vertical
    comment thread line with the comment reply box.

    When called as {{ comment.level|hline_div }} produces the string:

        '<div class="line-{comment.level}"></div>'
    """
    return mark_safe(f'<div class="{prefix}{level}"></div>')


@register.filter
def get_top_comment(reply_stack):
    return reply_stack[-1]


@register.filter
def pop_comments_lte(reply_stack, level_lte=0):
    comments_lte = []
    try:
        while True:
            comment = reply_stack.pop()
            if comment.level < level_lte:
                break
            comments_lte.append(comment)
    finally:
        return comments_lte


@register.simple_tag(takes_context=True)
def push_comment(context, comment):
    context['reply_stack'].append(comment)
    return ""


@register.filter
def get_comment(comment_id: str):
    return get_comment_model().objects.get(pk=int(comment_id))


# ----------------------------------------------------------------------
@register.inclusion_tag('django_comments_xtd/only_users_can_post.html')
def render_only_users_can_post_template(object):
    return {'html_id_suffix': get_html_id_suffix(object)}
