from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Business(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    street = models.CharField(max_length=200, blank=True, null=True)
    house_number = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='business_images/', null=True, blank=True)

class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    is_customer = models.BooleanField(default=True)
    is_supplier = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='contact_images/', null=True, blank=True)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_credit = models.BooleanField(default=False)

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_credit = models.BooleanField(default=False)

class Cash(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=16)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

def get_expiration_date():
    return timezone.now() + timezone.timedelta(minutes=40320)

class License(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_pro = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(default=get_expiration_date)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)