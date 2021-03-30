from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(default = "test-category", unique = True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class Product(models.Model):
    img = models.ImageField(upload_to='productImages/', default = 'default.png')
    title = models.CharField(max_length = 50, unique = True)
    price = models.FloatField()
    discounted_price = models.FloatField(blank = True, null = True)
    category = models.ForeignKey(Category, related_name = "products", on_delete = models.CASCADE, default = 0)
    slug = models.SlugField(default = "test-product", unique = True)
    description = models.TextField(default = "Please enter the description about the product. It should give an overview about the product, how popular the product is and so on..")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """ returns URL compatable Category and Product slug"""
        return f'/{self.category.slug}/{self.slug}'

    def displayDescription(self):
        """ returns Description of Product in formatted form for display"""
        return self.description.split('\\n')

    def get_single_savings(self):
        """returns discount on singular product"""
        return self.price - self.discounted_price

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    # "done" is used by the admin for his/her reference. Can be used in the code for future implementation

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price_for_item(self):
        return self.quantity * self.item.discounted_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price_for_item()

    def get_final_price(self):
        if self.item.discounted_price:
            return self.get_total_discount_price_for_item()
        return self.get_total_item_price()


class Order(models.Model):
    order_unique_num = models.CharField(max_length = 10, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    payment = models.ForeignKey('Payment', on_delete = models.SET_NULL, blank = True, null = True )
    coupon = models.ForeignKey('Coupon', on_delete = models.SET_NULL, blank = True, null = True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_without_coupon(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_grand_total(self):
        total = self.get_total_without_coupon()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_cart_items_num(self):
        sum = 0
        if self.items.exists():
            sum = 0
            for i in self.items.all():
                sum += i.quantity
        return sum

    def get_total_savings(self):
        savings = 0
        for order_item in self.items.all():
            if order_item.item.discounted_price:
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
        return f"{self.user.username} --> ₹  {self.amount}"


class Coupon(models.Model):
    coupon_code = models.CharField(max_length = 20, unique = True)
    amount = models.FloatField()
    active = models.BooleanField(default=True)

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
        return f'{self.address_1}\n{self.address_2}\n{self.city}, {self.state} - {self.zip}\n'

    class Meta:
        verbose_name_plural = 'Addresses'
