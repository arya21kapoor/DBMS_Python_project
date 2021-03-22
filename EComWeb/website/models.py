from django.db import models
from django.shortcuts import reverse
from django.conf import settings

class Category(models.Model):
    title = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(default = "test-category", unique = True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.slug


class Product(models.Model):
    imgProductImage = models.ImageField(upload_to='productImages/', default = 'default.png')
    title = models.CharField(max_length = 50, unique = True)
    price = models.FloatField()
    discountPrice = models.FloatField(blank = True, null = True)
    category = models.ForeignKey(Category, related_name = "products", on_delete = models.CASCADE, default = 0)
    slug = models.SlugField(default = "test-product", unique = True)
    description = models.TextField(default = "This is a the place where you have to enter the description about the product. Like the ingredients used how popular the product is")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}'

    def displayDescription(self):
        return self.description.split('\\n')

    def get_add_to_cart_url(self):
        return reverse("webiste:add_to_cart", kwargs={'slug': self.slug,})
        #return f'/{self.category.slug}/{self.slug}'

    def get_single_save(self):
        return self.price - self.discountPrice

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discountPrice

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discountPrice:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    payment = models.ForeignKey('Payment', on_delete = models.SET_NULL, blank = True, null = True )
    coupon = models.ForeignKey('Coupon', on_delete = models.SET_NULL, blank = True, null = True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    order_unique_num = models.CharField(max_length = 10, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total_without_coupon(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_total(self):
        total = self.get_total_without_coupon()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_cart_items(self):
        sum = 0
        if self.items.exists():
            sum = 0
            for i in self.items.all():
                sum += i.quantity
        return sum

    def get_total_savings(self):
        savings = 0
        for order_item in self.items.all():
            if order_item.item.discountPrice:
                savings += order_item.get_amount_saved()

        if self.coupon:
            savings += self.coupon.amount
        return savings


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length = 50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    coupon_code = models.CharField(max_length = 20, unique = True)
    amount = models.FloatField()

    def __str__(self):
        return self.coupon_code


ADDRESS_CHOICES = (
    ("S", "Shipping"),
    ("B", "Billing")
)

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length = 70)
    address_2 = models.CharField(max_length = 70)
    city = models.CharField(max_length = 30)
    state = models.CharField(max_length = 30)
    zip = models.CharField(max_length = 6)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'
