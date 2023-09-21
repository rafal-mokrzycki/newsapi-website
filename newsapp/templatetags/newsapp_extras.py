from django import template

register = template.Library()


@register.filter(name="myDate")
def myDate(value):
    # arg is optional and not needed but you could supply your own formatting if you want.
    dateformatted = value.strftime("%I:%M %p EDT, %a %B %e, %Y")
    return dateformatted
