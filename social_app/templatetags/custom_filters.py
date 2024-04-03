# I wrote this code

from django import template
from social_app.models import Like

register = template.Library()

@register.filter(name='has_liked')
def has_liked(status, user):
    return Like.objects.filter(post=status, user=user).exists()

# end of code I wrote