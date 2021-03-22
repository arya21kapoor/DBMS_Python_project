from django import template
from website.models import Order

register = template.Library()

# @register.filter
# def cart_item_count(user):
#     if user.is_authenticated:
#         qs = Order.objects.filter(user=user, ordered=False)
#         if qs.exists():
#             return qs[0].items.count()
#     return 0

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        sum = 0
        if qs.exists():
            for i in qs[0].items.all():
                sum += i.quantity
            return sum
    return 0

@register.filter
def past_orders_present(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=True)
        if qs.exists():
            return True
    return False
