from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.conf import settings

class Business(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

class Expense(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

class Card(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=16)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

def get_expiration_date():
    return timezone.now() + timezone.timedelta(minutes=40320)

class License(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_pro = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(default=get_expiration_date)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

def redimensionar_imagen(imagen, ancho=800, alto=600):
    if not imagen:
        return None
        
    img = Image.open(imagen)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Redimensionar manteniendo la proporción
    img.thumbnail((ancho, alto))
    
    # Optimizar y comprimir
    output = BytesIO()
    # Reducimos la calidad a 60% para menor peso
    img.save(output, format='JPEG', quality=60, optimize=True)
    output.seek(0)
    
    # Generar nuevo nombre para la imagen optimizada
    nombre_original = imagen.name
    nombre_base = nombre_original.split('.')[0]
    nuevo_nombre = f"{nombre_base}_optimized.jpg"
    
    return File(output, name=nuevo_nombre)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'