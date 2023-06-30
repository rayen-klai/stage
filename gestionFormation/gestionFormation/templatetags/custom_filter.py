from django import template

register = template.Library()

@register.filter
def get_val(dictionary, key):
    return dictionary.get(str(key))
