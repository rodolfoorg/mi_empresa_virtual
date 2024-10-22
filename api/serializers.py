from rest_framework import serializers
from api.models import Producto, Venta

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio']  # Ajusta estos campos según tu modelo

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total']  # Ajusta estos campos según tu modelo