from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Card, Expense
from ..serializers import CardSerializer, ExpenseSerializer
from ..mixins import BusinessFilterMixin

class CardViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = CardSerializer
    queryset = Card.objects.none()

    def get_queryset(self):
        return Card.objects.filter(business__user=self.request.user)

class ExpenseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.none()

    def get_queryset(self):
        return Expense.objects.filter(business__user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            expense = serializer.save()
            if hasattr(expense, 'card') and expense.card:
                card = expense.card
                card.balance -= expense.amount
                card.save()

    @action(detail=True, methods=['post'])
    def undo_expense(self, request, pk=None):
        try:
            with transaction.atomic():
                expense = self.get_object()
                card_id = request.data.get('card_id')
                
                if not card_id:
                    raise ValueError("Debe seleccionar una tarjeta para la devolución")
                
                try:
                    card = Card.objects.select_for_update().get(id=card_id)
                    previous_balance = card.balance
                    card.balance += expense.amount
                    card.save()
                    print(f"Card {card.id} balance updated: {previous_balance} -> {card.balance}")
                except Card.DoesNotExist:
                    raise ValueError("La tarjeta seleccionada no existe")
                except Exception as e:
                    raise ValueError(f"Error al actualizar el saldo de la tarjeta: {str(e)}")

                response_data = {
                    'message': 'Gasto deshecho exitosamente',
                    'amount': float(expense.amount),
                    'card_id': card.id,
                    'previous_balance': float(previous_balance),
                    'new_balance': float(card.balance)
                }

                expense.delete()
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error undoing expense: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )