from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from ..models import Product, Business
from ..serializers import ProductSerializer, BusinessSerializer


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            Q(is_public=True) &  # Producto público
            Q(business__is_public=True) &  # Negocio público
            Q(business__user__license__expiration_date__gt=timezone.now()) &  # Licencia válida
            ~Q(business__isnull=True)  # Asegurarse de que el negocio existe
        ).select_related('business', 'business__user')

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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Business.objects.filter(
            is_public=True,
            user__license__expiration_date__gt=timezone.now()
        )

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtener todos los productos públicos de un negocio específico"""
        business = self.get_object()
        products = Product.objects.filter(
            business=business,
            is_public=True,
            business__is_public=True
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