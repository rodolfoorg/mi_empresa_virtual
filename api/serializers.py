from rest_framework import serializers
from api.models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
import re
from django.contrib.auth import authenticate

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

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'  

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'  

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'  

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'  

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'  

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
            else:
                raise serializers.ValidationError(
                    'Credenciales incorrectas'
                )
        else:
            raise serializers.ValidationError(
                'Debe proporcionar tanto usuario/email como contraseña'
            )

        data['user'] = user
        return data