from django.contrib import admin
from .models import Product, Category, OrderItem, Order, Payment, Coupon, Address
from django.contrib.auth.models import Group
# Register your models here.\


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'address_1',
        'address_2',
        'city',
        'state',
        'zip',
        'address_type',
        'default',
        'used'
    ]
    list_filter = ['user', 'default', 'address_type']
    # search_fields = ['user', 'default', 'address_type']

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'payment',
        'ordered',
        'delivered',
    ]
    list_filter = ['user','ordered', 'delivered',]
    # search_fields = ['user', 'ordered', 'delivered',]

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)

admin.site.unregister(Group)
