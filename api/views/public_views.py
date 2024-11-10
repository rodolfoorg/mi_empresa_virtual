from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from ..models import Product, Business
from ..serializers import ProductSerializer, BusinessSerializer
from ..licencePersmission import HasValidLicenseForPublic


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.none()
    permission_classes = [HasValidLicenseForPublic]

    def get_queryset(self):
        # Primero filtramos productos públicos
        queryset = Product.objects.filter(is_public=True)
        
        # Filtramos productos de negocios con licencias válidas
        queryset = queryset.filter(business__user__license__expiration_date__gt=timezone.now())
        
        # Búsqueda por nombre o descripción
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filtrar por categoría
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
            
        # Filtrar por rango de precios
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Ordenar resultados
        ordering = self.request.query_params.get('ordering', '-created_at')
        return queryset.order_by(ordering)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Obtener todas las categorías disponibles"""
        categories = Product.objects.filter(
            is_public=True,
            business__user__license__expiration_date__gt=timezone.now()
        ).values_list('category', flat=True).distinct()
        return Response(list(categories))

class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusinessSerializer
    queryset = Business.objects.none()
    permission_classes = [HasValidLicenseForPublic]

    def get_queryset(self):
        queryset = Business.objects.filter(is_public=True)
        
        # Búsqueda por nombre o descripción
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        # Filtrar por tipo de negocio
        business_type = self.request.query_params.get('type', None)
        if business_type:
            queryset = queryset.filter(business_type=business_type)
            
        # Filtrar por ubicación
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtener todos los productos públicos de un negocio específico"""
        business = self.get_object()
        products = Product.objects.filter(
            business=business,
            is_public=True
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def types(self, request):
        """Obtener todos los tipos de negocios disponibles"""
        business_types = Business.objects.filter(is_public=True).values_list(
            'business_type', flat=True).distinct()
        return Response(list(business_types))

    @action(detail=False, methods=['get'])
    def locations(self, request):
        """Obtener todas las ubicaciones disponibles"""
        locations = Business.objects.filter(is_public=True).values_list(
            'location', flat=True).distinct()
        return Response(list(locations)) 