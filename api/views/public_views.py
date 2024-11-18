from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from ..models import Product, Business, Order
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
            image_url = serializers.SerializerMethodField()
            
            def get_image_url(self, obj):
                if obj.image:
                    return obj.image.url if hasattr(obj.image, 'url') else None
                return None
            
            class Meta(ProductSerializer.Meta):
                fields = ProductSerializer.Meta.fields + ['business_id', 'business_name', 'image_url']
        
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
        return Business.objects.filter(is_public=True)

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

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def track_order(request, tracking_code):
    try:
        order = Order.objects.select_related('business').prefetch_related('items__product').get(
            tracking_code=tracking_code
        )
        
        return Response({
            'tracking_code': order.tracking_code,
            'status': order.get_status_display(),
            'status_code': order.status,
            'customer_name': order.customer_name,
            'business_name': order.business.name,
            'created_at': order.created_at,
            'delivery_type': order.get_delivery_type_display(),
            'delivery_address': order.delivery_address,
            'delivery_municipality': order.delivery_municipality,
            'delivery_notes': order.delivery_notes,
            'pickup_time': order.pickup_time,
            'total_amount': str(order.total_amount),
            'items': [{
                'name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal)
            } for item in order.items.all()]
        })
    except Order.DoesNotExist:
        return Response(
            {'error': 'Código de seguimiento no válido'}, 
            status=status.HTTP_404_NOT_FOUND
        )