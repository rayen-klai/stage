from django import template
from user.models import Profile
register = template.Library()

@register.filter
def get_nompreById(id):
    u = Profile.objects.get(id=id)
    return u.last_name + ' ' + u.first_name

@register.filter
def get_ielement(l,i):
    return l[i]

@register.filter
def get_p(l):
    return l[0]

@register.filter
def get_id(n):
    return n.id

@register.filter
def get_nom(n):
    return n.last_name + ' ' +  n.first_name
@register.filter
def get_r(l):
    print(l)
    return l[1]



@register.filter
def get_val(dictionary, key):
    if(isinstance(dictionary.get(str(key)), list)):
       return 1
    return dictionary.get(str(key))

@register.filter
def subtract(value, arg):
    participants_enc = {key: value for key, value in arg.items() if value != 0}
    user_ids_enc = participants_enc.keys()
    participants_enc = [Profile.objects.get(id=key) for key in user_ids_enc]
    return value - len(participants_enc) 


@register.simple_tag
def define(val=None):
  return val