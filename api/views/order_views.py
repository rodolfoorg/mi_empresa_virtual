from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Order, Business, OrderItem, Product
from ..serializers import OrderSerializer
from rest_framework.decorators import action
from django.db import transaction

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(business=self.request.user.business)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business')
        
        # Debug logs
        print(f"Business ID recibido: {business_id}")
        print(f"Datos completos recibidos: {request.data}")

        if not business_id:
            return Response(
                {'business': ['Se requiere el ID del negocio']}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            business = Business.objects.get(id=business_id)
            print(f"Negocio encontrado: {business.name}")
        except Business.DoesNotExist:
            return Response(
                {'business': ['Negocio no encontrado']}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Usar transacción para asegurar la integridad de los datos
        with transaction.atomic():
            try:
                # Crear la orden primero
                order_data = request.data.copy()
                items_data = order_data.pop('items', [])
                
                order = Order.objects.create(
                    business=business,
                    customer_name=order_data.get('customer_name'),
                    customer_phone=order_data.get('customer_phone'),
                    delivery_type=order_data.get('delivery_type'),
                    delivery_address=order_data.get('delivery_address'),
                    delivery_municipality=order_data.get('delivery_municipality'),
                    delivery_notes=order_data.get('delivery_notes'),
                    pickup_time=order_data.get('pickup_time'),
                )

                # Crear los items de la orden
                total_amount = 0
                for item_data in items_data:
                    product = Product.objects.get(id=item_data['product'])
                    quantity = item_data['quantity']
                    unit_price = float(item_data['unit_price'])
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price
                    )
                    total_amount += quantity * unit_price

                # Actualizar el total de la orden
                order.total_amount = total_amount
                order.save()

                # Enviar email
                try:
                    items_text = "\n".join([
                        f"- {item.quantity}x {item.product.name} (${item.unit_price})"
                        for item in order.items.all()
                    ])

                    delivery_info = (
                        f"Dirección: {order.delivery_address}\n"
                        f"Municipio: {order.delivery_municipality}"
                        if order.delivery_type == 'delivery'
                        else f"Hora de recogida: {order.pickup_time}"
                    )

                    subject = f'Nuevo pedido pendiente - {order.tracking_code}'
                    message = f'''
                    ¡Nuevo Pedido en {business.name}!

                    Código de seguimiento: {order.tracking_code}

                    Información del cliente:
                    - Nombre: {order.customer_name}
                    - Teléfono: {order.customer_phone}
                    - Tipo de entrega: {'Entrega a domicilio' if order.delivery_type == 'delivery' else 'Recoger en tienda'}
                    {delivery_info}

                    Productos:
                    {items_text}

                    Total: ${order.total_amount}

                    Por favor, revisa y procesa este pedido lo antes posible.
                    '''

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[business.user.email],
                        fail_silently=False,
                    )

                except Exception as e:
                    print(f"Error al enviar el email: {str(e)}")
                    # Continuamos aunque falle el email

                # Serializar la respuesta
                serializer = self.get_serializer(order)
                return Response({
                    'tracking_code': order.tracking_code,
                    'message': 'Orden creada exitosamente',
                    'order': serializer.data
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"Error al crear la orden: {str(e)}")
                return Response({
                    'error': f'Error al crear la orden: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        order = self.get_object()
        order.status = request.data.get('status')
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
