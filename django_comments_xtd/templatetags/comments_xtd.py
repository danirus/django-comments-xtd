import hashlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import re

from django.contrib.contenttypes.models import ContentType
from django.template import (Library, Node, TemplateSyntaxError,
                             Variable, loader)
from django.utils.safestring import mark_safe

from django_comments_xtd import get_model as get_comment_model
from django_comments_xtd.conf import settings

from ..utils import import_formatter


XtdComment = get_comment_model()

formatter = import_formatter()

register = Library()


# ----------------------------------------------------------------------
class XtdCommentCountNode(Node):
    """Store the number of XtdComments for the given list of app.models"""

    def __init__(self, as_varname, content_types):
        """Class method to parse get_xtdcomment_list and return a Node."""
        self.as_varname = as_varname
        self.qs = XtdComment.objects.for_content_types(content_types)

    def render(self, context):
        context[self.as_varname] = self.qs.count()
        return ''


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


register.tag(get_xtdcomment_count)


# ----------------------------------------------------------------------
class BaseLastXtdCommentsNode(Node):
    """Base class to deal with the last N XtdComments for a list of app.model"""

    def __init__(self, count, content_types, template_path=None):
        """Class method to parse get_xtdcomment_list and return a Node."""
        try:
            self.count = int(count)
        except:
            self.count = Variable(count)

        self.content_types = content_types
        self.template_path = template_path


class RenderLastXtdCommentsNode(BaseLastXtdCommentsNode):

    def render(self, context):
        if not isinstance(self.count, int):
            self.count = int(self.count.resolve(context))

        self.qs = XtdComment.objects.for_content_types(
            self.content_types)[:self.count]

        strlist = []
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
            strlist.append(
                loader.render_to_string(
                    template_arg, {"comment": xtd_comment}, context))
        return ''.join(strlist)


class GetLastXtdCommentsNode(BaseLastXtdCommentsNode):

    def __init__(self, count, as_varname, content_types):
        super(GetLastXtdCommentsNode, self).__init__(count, content_types)
        self.as_varname = as_varname

    def render(self, context):
        if not isinstance(self.count, int):
            self.count = int(self.count.resolve(context))
        self.qs = XtdComment.objects.for_content_types(
            self.content_types)[:self.count]
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
                "%r tag has non-existant content-type: '%s.%s'" % (
                    tagname, app, model))
    return content_types


def render_last_xtdcomments(parser, token):
    """
    Render the last N XtdComments through the
      ``comments_xtd/comment.html`` template

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
            template = tokens[token_using+1].strip('" ')
        except IndexError:
            raise TemplateSyntaxError("Last argument in %r tag must be a "
                                      "relative template path" % tokens[0])
    except ValueError:
        content_types = _get_content_types(tokens[0], tokens[3:])
        template = None

    return RenderLastXtdCommentsNode(count, content_types, template)


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


register.tag(render_last_xtdcomments)
register.tag(get_last_xtdcomments)


# ----------------------------------------------------------------------
class GetXtdCommentTreeNode(Node):
    def __init__(self, obj, var_name, with_participants):
        self.obj = Variable(obj)
        self.var_name = var_name
        self.with_participants = with_participants

    def render(self, context):
        obj = self.obj.resolve(context)
        ctype = ContentType.objects.get_for_model(obj)
        qs = XtdComment.objects.filter(content_type=ctype,
                                       object_pk=obj.pk,
                                       site__pk=settings.SITE_ID,
                                       is_public=True)
        diclist = XtdComment.tree_from_queryset(qs, self.with_participants)
        context[self.var_name] = diclist
        return ''


def get_xtdcomment_tree(parser, token):
    """
    Adds to the template context a list of XtdComment dictionaries for the
    given object. The optional argument *with_participants* adds a list
    'likedit' with the users who liked the comment and a list 'dislikedit'
    with the users who disliked the comment.

    Each XtdComment dictionary has the following attributes::
        {
            'comment': xtdcomment object,
            'children': [ list of child xtdcomment dicts ]
        }

    When called with-counters each XtdComment dictionary will look like::
        {
            'comment': xtdcomment object,
            'children': [ list of child xtdcomment dicts ],
            'likedit': [user_object_a, user_object_b, ...],
            'dislikedit': [user_object_x, user_object_y, ...],
        }

    Syntax::
        {% get_xtdcomment_tree for [object] as [varname] [with_participants] %}
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
    if args.strip().endswith('with_participants'):
        with_participants = True
    else:
        with_participants = False
    return GetXtdCommentTreeNode(obj, var_name, with_participants)


register.tag(get_xtdcomment_tree)


# ----------------------------------------------------------------------
def render_with_filter(markup_filter, lines):
    try:
        if formatter:
            return mark_safe(formatter("\n".join(lines),
                                       filter_name=markup_filter))
        else:
            raise TemplateSyntaxError("In order to use this templatetag you "
                                      "need django-markup, docutils and "
                                      "markdown installed")
    except ValueError as exc:
        output = "<p>Warning: %s</p>" % exc
        return output


def render_markup_comment(value):
    """
    Renders a comment using a markup language specified in the first line of
    the comment.

    Template Syntax::

        {{ comment.comment|render_markup_comment }}

    The first line of the comment field must start with the name of the markup
    language unless the COMMENTS_XTD_MARKUP_FALLBACK_FILTER setting is not None.

    A comment like::

        comment = r'''#!markdown\n\rAn [example](http://url.com/ "Title")'''

    Would be rendered as a markdown text, producing the output::

        <p><a href="http://url.com/" title="Title">example</a></p>

    A default markup language can be specified with the
    COMMENTS_XTD_MARKUP_FALLBACK_FILTER setting to force a default filter.
    """
    lines = value.splitlines()
    rawstr = r"""^#!(?P<markup_filter>\w+)$"""
    match_obj = re.search(rawstr, lines[0])
    if match_obj:
        markup_filter = match_obj.group('markup_filter')
        return render_with_filter(markup_filter, lines[1:])
    elif settings.COMMENTS_XTD_MARKUP_FALLBACK_FILTER:
        markup_filter = settings.COMMENTS_XTD_MARKUP_FALLBACK_FILTER
        return render_with_filter(markup_filter, lines)
    else:
        return value

register.filter(render_markup_comment)


# ----------------------------------------------------------------------
def xtd_comment_gravatar_url(email, size=48):
    return ("http://www.gravatar.com/avatar/%s?%s&d=mm" %
            (hashlib.md5(email.lower().encode('utf-8')).hexdigest(),
             urlencode({'s': str(size)})))


register.filter(xtd_comment_gravatar_url)


# ----------------------------------------------------------------------
def xtd_comment_gravatar(email, size=48):
    url = xtd_comment_gravatar_url(email, size)
    return mark_safe('<img src="%s" height="%d" width="%d">' %
                     (url, size, size))


register.filter(xtd_comment_gravatar)
