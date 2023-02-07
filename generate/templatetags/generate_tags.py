from django import template

register = template.Library()


@register.filter
def get_item(dictionary, value):
    try:
        return dictionary.get(str(value)) if dictionary.get(str(value)) else {}
    except:
        return {}


@register.filter
def get_text_without_n(string):
    return string.replace('\n', '   ')
