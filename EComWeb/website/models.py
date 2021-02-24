from django.db import models
from django.shortcuts import reverse
from django.conf import settings

class Category(models.Model):
    title = models.CharField(max_length = 100, unique = True)
    slug = models.SlugField(default = "test-category", unique = True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.slug


class Product(models.Model):
    imgProductImage = models.ImageField(upload_to='productImages/', default = 'default.png')
    title = models.CharField(max_length = 100, unique = True)
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

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    #order_id = models.ForeignKey(Order, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
