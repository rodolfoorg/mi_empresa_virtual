from rest_framework import viewsets
from api.models import Producto, Venta
from .serializers import ProductoSerializer, VentaSerializer
from django.shortcuts import render

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

def api_welcome(request):
    return render(request, 'welcome.html')