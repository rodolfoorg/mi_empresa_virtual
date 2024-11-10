from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from ..models import Product, Business
from ..serializers import ProductSerializer, BusinessSerializer
from ..licencePersmission import HasValidLicenseForPublic


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [HasValidLicenseForPublic]

    def get_queryset(self):
        # Primero filtramos productos públicos y hacemos select_related para optimizar
        queryset = Product.objects.filter(
            is_public=True
        ).select_related('business', 'business__user')
        
        # Filtramos productos de negocios con licencias válidas
        queryset = queryset.filter(
            business__user__license__expiration_date__gt=timezone.now()
        )
        
        return queryset

    def get_serializer_class(self):
        class PublicProductWithBusinessSerializer(ProductSerializer):
            business_id = serializers.IntegerField(source='business.id', read_only=True)
            business_name = serializers.CharField(source='business.name', read_only=True)
            
            class Meta(ProductSerializer.Meta):
                fields = ProductSerializer.Meta.fields + ['business_id', 'business_name']
        
        return PublicProductWithBusinessSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['include_business_id'] = True
        context['include_business_details'] = True
        return context

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
    queryset = Business.objects.all()
    permission_classes = [HasValidLicenseForPublic]

    def get_queryset(self):
        # Filtrar negocios públicos con licencias válidas
        queryset = Business.objects.filter(
            is_public=True,
            user__license__expiration_date__gt=timezone.now()
        )
        
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
        business_types = Business.objects.filter(
            is_public=True,
            user__license__expiration_date__gt=timezone.now()
        ).values_list('business_type', flat=True).distinct()
        return Response(list(business_types))

    @action(detail=False, methods=['get'])
    def locations(self, request):
        """Obtener todas las ubicaciones disponibles"""
        locations = Business.objects.filter(
            is_public=True,
            user__license__expiration_date__gt=timezone.now()
        ).values_list('location', flat=True).distinct()
        return Response(list(locations))