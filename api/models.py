from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files import File
import uuid
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_product_limit(business_id, license_type):
    product_count = Product.objects.filter(business_id=business_id).count()
    limits = {
        'basico': 50,
        'avanzado': 100, 
        'pro': 500
    }
    if product_count >= limits[license_type]:
        raise ValidationError(f'No puedes crear más de {limits[license_type]} productos con el plan {license_type}.')

class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Cambiado a OneToOneField
    owner = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True, default="No especificado")
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    street = models.CharField(max_length=200, blank=True, null=True)
    house_number = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='business_images/', null=True, blank=True)

    class Meta:
        # Eliminamos unique_together ya que OneToOneField ya garantiza la unicidad
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default='Otros', blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_public = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    class Meta:
        unique_together = ['business', 'name']

    def clean(self):
        if not self.pk:  # Solo validar al crear nuevo producto
            license = License.objects.get(user=self.business.user)
            validate_product_limit(self.business_id, license.plan)
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Contact(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    is_customer = models.BooleanField(default=True)
    is_supplier = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to='contact_images/', null=True, blank=True)

class Card(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=16)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        unique_together = ['business', 'name']

class Sale(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_credit = models.BooleanField(default=False)

class Purchase(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_credit = models.BooleanField(default=False)

class Expense(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default='Otros', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

def get_expiration_date():
    return timezone.now() + timezone.timedelta(days=7)

class License(models.Model):
    PLAN_CHOICES = [
        ('basico', 'Básico'),
        ('avanzado', 'Avanzado'),
        ('pro', 'Pro')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basico')
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(default=get_expiration_date)

    @property
    def tiempo_restante(self):
        ahora = timezone.now()
        if self.expiration_date > ahora:
            return self.expiration_date - ahora
        return timezone.timedelta(0)

@receiver(post_save, sender=User)
def crear_licencia_basica(sender, instance, created, **kwargs):
    if created:
        License.objects.create(
            user=instance,
            plan='basico',
            start_date=timezone.now(),
            expiration_date=timezone.now() + timezone.timedelta(days=7)
        )

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

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token de verificación para {self.user.email}"

class LicenseRenewal(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_code = models.CharField(max_length=100)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendiente')
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    days_requested = models.IntegerField(default=30)  # Por defecto 30 días

    def __str__(self):
        return f"Renovación de {self.user.username} - {self.status}"

    class Meta:
        ordering = ['-requested_at']