from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Sale, Purchase, Product, Card
from ..serializers import SaleSerializer, PurchaseSerializer
from ..mixins import BusinessFilterMixin
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

class SaleViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()

    def get_queryset(self):
        return Sale.objects.filter(business__user=self.request.user)

    @action(detail=False, methods=['post'])
    def register_sale(self, request):
        try:
            with transaction.atomic():
                # Añadir el business del usuario actual a los datos
                data = request.data.copy()
                data['business'] = request.user.business.id
                
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    sale = serializer.save()
                    
                    # Actualizar el stock del producto
                    product = Product.objects.get(id=sale.product.id)
                    product.stock -= sale.quantity
                    product.save()
                    
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def undo_sale(self, request, pk=None):
        try:
            with transaction.atomic():
                sale = self.get_object()
                quantity = sale.quantity
                unit_price = sale.unit_price
                product_id = sale.product_id
                card_id = sale.card_id if hasattr(sale, 'card') else None
                is_credit = sale.is_credit

                # Actualizar stock del producto si existe
                try:
                    product = Product.objects.get(id=product_id)
                    product.stock += quantity
                    product.save()
                except Product.DoesNotExist:
                    pass

                # Actualizar saldo de la tarjeta si aplica
                if not is_credit and card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        total_amount = quantity * unit_price
                        card.balance -= total_amount
                        card.save()
                    except Card.DoesNotExist:
                        pass

                # Eliminar la venta
                sale.delete()
                return Response({'message': 'Venta deshecha exitosamente'}, 
                              status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                sale = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PurchaseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Purchase.objects.all()

    def get_queryset(self):
        return Purchase.objects.filter(business__user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                purchase = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error en create purchase: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def undo_purchase(self, request, pk=None):
        try:
            with transaction.atomic():
                purchase = self.get_object()
                quantity = purchase.quantity
                unit_price = purchase.unit_price
                product_id = purchase.product_id
                
                new_card_id = request.data.get('card_id')
                original_card_id = purchase.card_id if hasattr(purchase, 'card') else None
                card_id = new_card_id or original_card_id
                
                is_credit = purchase.is_credit

                if not is_credit and not card_id:
                    return Response(
                        {'error': 'Se requiere una tarjeta para deshacer una compra que no fue a crédito'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    product = Product.objects.get(id=product_id)
                    if product.stock < quantity:
                        return Response(
                            {'error': 'No hay suficiente stock para deshacer la compra'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    product.stock -= quantity
                    product.save()
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'El producto ya no existe'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not is_credit and card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        total_amount = quantity * unit_price
                        card.balance += total_amount
                        card.save()
                    except Card.DoesNotExist:
                        return Response(
                            {'error': 'La tarjeta seleccionada no existe'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                purchase.delete()
                return Response(
                    {'message': 'Compra deshecha exitosamente'}, 
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )