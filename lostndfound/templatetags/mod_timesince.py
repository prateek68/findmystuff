from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter(name='ago')

def ago(date):
    """For removing the pesky little details."""
    ago = timesince(date)
    return ago.split(",")[0] + " ago"