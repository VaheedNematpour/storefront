from django.conf import settings
from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                MinValueValidator(1.00)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Customer(models.Model):
    MEMBER_BRONZE = 'B'
    MEMBER_GOLD = 'G'
    MEMBER_SILVER = 'S'

    MEMBERSHIP = {
        (MEMBER_BRONZE, 'Bronze'),
        (MEMBER_GOLD, 'Gold'),
        (MEMBER_SILVER, 'Silver')
    }

    phone = models.CharField(max_length=256)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP, default=MEMBER_BRONZE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ('view_history', 'Can view history')
        ]


class Address(models.Model):
    street = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class Order(models.Model):
    ORDER_COMPLETED = 'C'
    ORDER_FAILED = 'F'
    ORDER_PENDING = 'P'

    ORDER_STATUS = {
        (ORDER_COMPLETED, 'Completed'),
        (ORDER_FAILED, 'Failed'),
        (ORDER_PENDING, 'Pending')
    }

    placed_at = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(
        max_length=1, choices=ORDER_STATUS, default=ORDER_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=256)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
