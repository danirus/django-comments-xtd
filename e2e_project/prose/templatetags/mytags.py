import markdown
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = Library()


@stringfilter
@register.filter
def render_markdown(text):
    md = markdown.Markdown(extensions=["fenced_code"])
    return mark_safe(md.convert(text))
