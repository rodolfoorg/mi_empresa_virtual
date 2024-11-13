from rest_framework import serializers
from .models import (
    Product, Sale, Business, Purchase, Expense, Card, Contact, License,
    LicenseRenewal, Order, OrderItem
)
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
        fields = ['id', 'name', 'number', 'balance', 'business']
        read_only_fields = ['business']

    def validate(self, data):
        # Asegurar que balance tenga un valor por defecto si no se proporciona
        if 'balance' not in data:
            data['balance'] = 0
        return data

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("El balance no puede ser negativo")
        return value

    def to_representation(self, instance):
        # Para mostrar el balance formateado en la respuesta
        representation = super().to_representation(instance)
        representation['balance'] = float(representation['balance'])
        return representation

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
        fields = ['id', 'username', 'email', 'first_name', 'last_name','date_joined']
        read_only_fields = ['username', 'email']  # No permitir cambios en estos campos
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
            'username': {'required': False}
        }

    def update(self, instance, validated_data):
        # Actualizar solo los campos permitidos
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

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

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'tracking_code', 'business', 'business_name',
            'customer_name', 'customer_phone', 'delivery_type',
            'delivery_type_display', 'delivery_address',
            'delivery_municipality', 'delivery_notes', 'pickup_time',
            'status', 'status_display', 'created_at', 'updated_at',
            'total_amount', 'items', 'status_notes'
        ]
        read_only_fields = ['tracking_code', 'business', 'business_name']

    def create(self, validated_data):
        business = self.context.get('business')
        if not business:
            raise serializers.ValidationError({'business': 'Se requiere el negocio'})
        
        validated_data['business'] = business
        return super().create(validated_data)

    def validate(self, data):
        # Validar que haya items
        if not self.initial_data.get('items', []):
            raise serializers.ValidationError({
                'items': 'Debe incluir al menos un producto en el pedido'
            })
        
        # Validar tipo de entrega
        if data['delivery_type'] == 'delivery':
            if not data.get('delivery_address'):
                raise serializers.ValidationError({
                    'delivery_address': 'La dirección es requerida para entregas a domicilio'
                })
            if not data.get('delivery_municipality'):
                raise serializers.ValidationError({
                    'delivery_municipality': 'El municipio es requerido para entregas a domicilio'
                })
        else:  # pickup
            if not data.get('pickup_time'):
                raise serializers.ValidationError({
                    'pickup_time': 'La hora de recogida es requerida'
                })
        
        return data