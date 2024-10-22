from rest_framework import serializers
from api.models import *

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio']  

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'cantidad', 'precio_unitario', 'negocio', 'producto']  

class NegocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Negocio
        fields = ['id', 'usuario', 'nombre']  

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = ['id', 'negocio', 'producto', 'fecha', 'cantidad', 'precio_unitario']  

class EfectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Efectivo
        fields = ['id', 'usuario', 'cantidad']  

class TarjetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarjeta
        fields = ['id', 'usuario', 'nombre', 'numero', 'saldo']  

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = ['id', 'usuario', 'nombre', 'numero', 'es_cliente', 'es_proveedor']  