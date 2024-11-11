from rest_framework import serializers
from api.models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
import re
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'purchase_price', 
                 'sale_price', 'is_public', 'stock', 'created_at', 'image']
        read_only_fields = ['business']

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['business']

    def validate(self, data):
        # Verificar stock disponible
        product = Product.objects.get(id=data['product'].id)
        if product.stock < data['quantity']:
            raise serializers.ValidationError(
                f"Stock insuficiente. Solo hay {product.stock} unidades disponibles."
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['business'] = request.user.business
        
        with transaction.atomic():
            # Crear la venta
            sale = super().create(validated_data)
            
            # Actualizar el stock del producto
            product = Product.objects.get(id=sale.product.id)
            product.stock -= sale.quantity
            product.save()
            
            # Actualizar el saldo de la tarjeta si no es a crédito
            if not sale.is_credit and sale.card:
                card = Card.objects.get(id=sale.card.id)
                total_amount = sale.quantity * sale.unit_price
                card.balance += total_amount
                card.save()
            
            return sale

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'  

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['business']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['business'] = request.user.business
        
        with transaction.atomic():
            # Crear la compra
            purchase = super().create(validated_data)
            
            # Actualizar el stock del producto
            product = Product.objects.get(id=purchase.product.id)
            product.stock += purchase.quantity
            product.save()
            
            # Actualizar el saldo de la tarjeta si no es a crédito
            if not purchase.is_credit and purchase.card:
                card = Card.objects.get(id=purchase.card.id)
                total_amount = purchase.quantity * purchase.unit_price
                if card.balance < total_amount:
                    raise ValidationError("La tarjeta no tiene saldo suficiente")
                card.balance -= total_amount
                card.save()
            
            return purchase

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['business']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['business'] = request.user.business
        
        with transaction.atomic():
            # Crear el gasto
            expense = super().create(validated_data)
            
            # Si hay una tarjeta asociada, actualizar su saldo
            if expense.card:
                card = Card.objects.get(id=expense.card.id)
                if card.balance < expense.amount:
                    raise ValidationError("La tarjeta no tiene saldo suficiente")
                card.balance -= expense.amount
                card.save()
            
            return expense

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'  

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['business']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['business'] = request.user.business
        return super().create(validated_data)

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

class LicenseRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseRenewal
        fields = ['id', 'user', 'transaction_code', 'requested_at', 'status', 
                 'processed_at', 'notes', 'days_requested']
        read_only_fields = ['user', 'status', 'processed_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'required': True,
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message='Ya existe un usuario con este correo electrónico'
                    )
                ]
            }
        }

    def validate_username(self, value):
        # Verificar longitud mínima
        if len(value) < 3:
            raise serializers.ValidationError(
                'El nombre de usuario debe tener al menos 3 caracteres'
            )
        
        # Verificar que no empiece con número
        if value[0].isdigit():
            raise serializers.ValidationError(
                'El nombre de usuario no puede empezar con un número'
            )
        
        # Verificar caracteres permitidos
        if not all(c.isalnum() or c == '_' for c in value):
            raise serializers.ValidationError(
                'El nombre de usuario solo puede contener letras, números y guión bajo (_)'
            )
        
        return value

    def validate_email(self, value):
        # Validar formato de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError(
                'Por favor, introduce una dirección de correo electrónico válida'
            )
        return value

    def create(self, validated_data):
        # Simplificar el create, solo crear el usuario
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('username')
        password = data.get('password')

        if '@' in identifier:
            # Si es un email, buscar el usuario por email
            try:
                user = User.objects.get(email=identifier)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No existe una cuenta con este correo electrónico'
                )
        else:
            username = identifier

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        'Esta cuenta no está activada'
                    )
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError(
                    'Credenciales incorrectas'
                )
        else:
            raise serializers.ValidationError(
                'Debe proporcionar tanto usuario/email como contraseña'
            )