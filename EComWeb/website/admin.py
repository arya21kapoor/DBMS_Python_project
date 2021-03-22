# Registering models here.
from django.contrib import admin
from .models import Product, Category, OrderItem, Order, Payment, Coupon, Address
from django.contrib.auth.models import Group

# Below classes are made for better display of the admin
# Also for filtering according to the different fields

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'discountPrice', 'category']
    list_filter = ['category']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'done', 'user']
    list_filter = ['done']

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

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'payment',
        'ordered',
        'delivered',
    ]
    list_filter = ['user','ordered', 'delivered',]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)

admin.site.unregister(Group)
