import json
import hashlib
import re

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType
from django.template import (Library, Node, TemplateSyntaxError,
                             Variable, loader)
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_comments.models import CommentFlag
from django_comments_xtd import get_model as get_comment_model
from django_comments_xtd.api import frontend
from django_comments_xtd.models import LIKEDIT_FLAG, DISLIKEDIT_FLAG
from django_comments_xtd.utils import (
    get_app_model_options, get_current_site_id, get_html_id_suffix
)


XtdComment = get_comment_model()


register = Library()


# ----------------------------------------------------------------------
class XtdCommentCountNode(Node):
    """Store the number of XtdComments for the given list of app.models"""

    def __init__(self, as_varname, content_types):
        """Class method to parse get_xtdcomment_list and return a Node."""
        self.as_varname = as_varname
        self.qs = XtdComment.objects.for_content_types(content_types)

    def render(self, context):
        context[self.as_varname] = self.qs.filter(
                site=get_current_site_id(context.get('request'))
            ).count()
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

        self.qs = XtdComment.objects.for_content_types(
                self.content_types,
                site=get_current_site_id(context.get('request'))
            ).order_by('submit_date')[:self.count]

        strlist = []
        context_dict = context.flatten()
        for xtd_comment in self.qs:
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
        self.qs = XtdComment.objects.for_content_types(
                self.content_types,
                site=get_current_site_id(context.get('request'))
            )\
            .order_by('submit_date')[:self.count]
        context[self.as_varname] = self.qs
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
class RenderXtdCommentTreeNode(Node):
    def __init__(self, obj, cvars, allow_feedback=False, show_feedback=False,
                 allow_flagging=False, template_path=None):
        self.obj = Variable(obj) if obj else None
        self.cvars = self.parse_cvars(cvars)
        self.allow_feedback = allow_feedback
        self.show_feedback = show_feedback
        self.allow_flagging = allow_flagging
        self.template_path = template_path

    def parse_cvars(self, pairs):
        cvars = []
        for vname, vobj in [pair.split("=") for pair in pairs]:
            cvars.append((vname, Variable(vobj)))
        return cvars

    def render(self, context):
        context_dict = context.flatten()
        for attr in ['allow_flagging', 'allow_feedback', 'show_feedback']:
            context_dict[attr] = (getattr(self, attr, False) or
                                  context.get(attr, False))
        if self.obj:
            obj = self.obj.resolve(context)
            ctype = ContentType.objects.get_for_model(obj)
            flags_qs = CommentFlag.objects.filter(flag__in=[
                CommentFlag.SUGGEST_REMOVAL, LIKEDIT_FLAG, DISLIKEDIT_FLAG
            ]).prefetch_related('user')
            prefetch = Prefetch('flags', queryset=flags_qs)
            queryset = XtdComment\
                .objects\
                .prefetch_related(prefetch)\
                .filter(
                    content_type=ctype,
                    object_pk=obj.pk,
                    site__pk=get_current_site_id(context.get('request')),
                    is_public=True
                )
            comments = XtdComment.tree_from_queryset(
                queryset,
                with_flagging=self.allow_flagging,
                with_feedback=self.allow_feedback,
                user=context['user']
            )
            context_dict['comments'] = comments
        if self.cvars:
            for vname, vobj in self.cvars:
                context_dict[vname] = vobj.resolve(context)
        if not self.obj:
            # Then presume 'comments' exists in the context.
            try:
                ctype = context['comments'][0]['comment'].content_type
            except Exception:
                raise TemplateSyntaxError("'render_xtdcomment_tree' doesn't "
                                          "have 'comments' in the context and "
                                          "neither have been provided with the "
                                          "clause 'with'.")
        if self.template_path:
            template_arg = self.template_path
        else:
            template_arg = [
                "django_comments_xtd/%s/%s/comment_tree.html" % (
                    ctype.app_label, ctype.model),
                "django_comments_xtd/%s/comment_tree.html" % (
                    ctype.app_label,),
                "django_comments_xtd/comment_tree.html"
            ]
        html = loader.render_to_string(template_arg, context_dict)
        return html


class GetXtdCommentTreeNode(Node):
    def __init__(self, obj, var_name, with_feedback):
        self.obj = Variable(obj)
        self.var_name = var_name
        self.with_feedback = with_feedback

    def render(self, context):
        obj = self.obj.resolve(context)
        ctype = ContentType.objects.get_for_model(obj)
        flags_qs = CommentFlag.objects.filter(flag__in=[
            CommentFlag.SUGGEST_REMOVAL, LIKEDIT_FLAG, DISLIKEDIT_FLAG
        ]).prefetch_related('user')
        prefetch = Prefetch('flags', queryset=flags_qs)
        queryset = XtdComment\
            .objects\
            .prefetch_related(prefetch)\
            .filter(
                content_type=ctype,
                object_pk=obj.pk,
                site__pk=get_current_site_id(context.get('request')),
                is_public=True
            )
        dic_list = XtdComment.tree_from_queryset(
            queryset,
            with_feedback=self.with_feedback,
            user=context['user']
        )
        context[self.var_name] = dic_list
        return ''


@register.tag
def render_xtdcomment_tree(parser, token):
    """
    Render the nested comment tree structure posted to the given object.
    By default uses the template ``django_comments_xtd/comments_tree.html``.

    Syntax::

        {% render_xtdcomment_tree [for <object>] [with vname1=<obj1>
           vname2=<obj2>] [allow_feedback] [show_feedback] [allow_flagging]
           [using <template>] %}
        {% render_xtdcomment_tree with <varname>=<context-var> %}

    Example usage::

        {% render_xtdcomment_tree for object allow_feedback %}
        {% render_xtdcomment_tree with comments=comment.children %}
    """
    obj = None
    cvars = []
    allow_feedback = False
    show_feedback = False
    allow_flagging = False
    template_path = None
    tokens = token.contents.split()
    tag = tokens.pop(0)

    # There must be at least a 'for <object>' or a 'with vname=obj' clause.
    if len(tokens) < 2 or tokens[0] not in ["for", "with"]:
        raise TemplateSyntaxError("2nd and 3rd argument in %r must be either "
                                  "a 'for <object>' or a 'with vname=<obj>' "
                                  "clause." % tag)
    while tokens:
        token = tokens.pop(0)
        if token == "for":
            if tokens[0] != "with":
                obj = tokens[0]
            else:
                raise TemplateSyntaxError("3rd argument after 'for' in %r "
                                          "can't be reserved word 'with'."
                                          % tag)
        if token == "with":
            tail_tokens = ["allow_feedback", "show_feedback", "allow_flagging",
                           "using"]
            try:
                if tokens[0] not in tail_tokens:
                    while len(tokens) and tokens[0] not in tail_tokens:
                        pair = tokens.pop(0)
                        if pair.find("=") == -1:
                            raise Exception()
                        cvars.append(pair)
                else:
                    raise Exception()
            except Exception:
                raise TemplateSyntaxError("arguments after 'with' in %r "
                                          "must be pairs varname=obj." % tag)
        if token == "allow_feedback":
            allow_feedback = True
        if token == "show_feedback":
            show_feedback = True
        if token == "allow_flagging":
            allow_flagging = True
        if token == "using":
            try:
                template_path = tokens[0]
            except IndexError:
                raise TemplateSyntaxError("The relative path to the template "
                                          "is missing after 'using' in %r."
                                          % tag)
    return RenderXtdCommentTreeNode(obj, cvars,
                                    allow_feedback=allow_feedback,
                                    show_feedback=show_feedback,
                                    allow_flagging=allow_flagging,
                                    template_path=template_path)


@register.tag
def get_xtdcomment_tree(parser, token):
    """
    Add to the template context a list of XtdComment dictionaries for the
    given object. The optional argument *with_feedback* adds a list
    'likedit' with the users who liked the comment and a list 'dislikedit'
    with the users who disliked the comment.

    Each XtdComment dictionary has the following attributes::
        {
            'comment': xtdcomment object,
            'children': [ list of child xtdcomment dicts ]
        }

    When called with_feedback each XtdComment dictionary will look like::
        {
            'comment': xtdcomment object,
            'children': [ list of child xtdcomment dicts ],
            'likedit': [user_object_a, user_object_b, ...],
            'dislikedit': [user_object_x, user_object_y, ...],
        }

    Syntax::
        {% get_xtdcomment_tree for [object] as [varname] [with_feedback] %}
    Example usage::
        {% get_xtdcomment_tree for post as comment_list %}
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("%s tag requires arguments" %
                                  token.contents.split()[0])
    match = re.search(r'for (\w+) as (\w+)', args)
    if not match:
        raise TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    obj, var_name = match.groups()
    if args.strip().endswith('with_feedback'):
        with_feedback = True
    else:
        with_feedback = False
    return GetXtdCommentTreeNode(obj, var_name, with_feedback)


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
@register.inclusion_tag('django_comments_xtd/only_users_can_post.html')
def render_only_users_can_post_template(object):
    return {'html_id_suffix': get_html_id_suffix(object)}
