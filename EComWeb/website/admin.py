# Registering models here.
from django.contrib import admin
from .models import Product, Category, OrderItem, Order, Payment, Coupon, Address
from django.contrib.auth.models import Group

# Below classes are for better display of the admin
# Also for filtering according to the different fields

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'discounted_price', 'category']
    list_filter = ['category']
    search_fields = ['title']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'item', 'quantity']
    fields = ['user', 'item', 'quantity', 'ordered', 'done']
    list_display = ['item', 'quantity', 'done', 'user']
    list_filter = ['done']
    list_editable = ['done']
    search_fields = ['quantity', 'item__title', ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['order_unique_num', 'user', 'items', 'ordered_date', 'payment', 'coupon', 'shipping_address', 'billing_address', 'ordered']
    fields = ['order_unique_num', 'user', 'items', 'ordered_date', 'payment', 'coupon', 'shipping_address', 'billing_address', 'ordered', 'delivered']
    list_display = ['user', 'payment', 'ordered', 'delivered']
    list_filter = ['user','ordered', 'delivered']
    list_editable =['delivered']
    search_fields = ['order_unique_num']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ['stripe_charge_id', 'user', 'amount', 'timestamp']
    list_display = ['user', 'amount', 'timestamp']
    list_filter = ['user']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'amount', 'active']
    list_editable =['active']
    search_fields = ['coupon_code']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'address_1', 'address_2', 'city', 'state', 'zip', 'address_type', 'default', 'used']
    list_display = ['user', 'address_1', 'address_2', 'city', 'state', 'zip', 'address_type', 'default', 'used' ]
    list_filter = ['user', 'default', 'address_type']
    search_fields = ['address_1', 'address_2', 'city', 'state', 'zip']


admin.site.unregister(Group) # not imp for now
