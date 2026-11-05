"""Template filter для рендеринга markdown в HTML."""
import markdown

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_markdown(value: str) -> str:
    """Рендерит markdown-текст в HTML."""
    if not value:
        return ''
    html = markdown.markdown(
        value,
        extensions=['extra', 'codehilite'],
    )
    return mark_safe(html)
