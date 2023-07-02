from django import template
from user.models import Profile
register = template.Library()

@register.filter
def get_val(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def subtract(value, arg):
    participants_enc = {key: value for key, value in arg.items() if value != 0}
    user_ids_enc = participants_enc.keys()
    participants_enc = [Profile.objects.get(id=key) for key in user_ids_enc]
    return value - len(participants_enc) 