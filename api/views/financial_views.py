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

    @action(detail=True, methods=['post'])
    def undo_expense(self, request, pk=None):
        try:
            with transaction.atomic():
                expense = self.get_object()
                amount = expense.amount
                card_id = expense.card_id if hasattr(expense, 'card') else None

                if card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        card.balance += amount
                        card.save()
                    except Card.DoesNotExist:
                        pass

                expense.delete()
                return Response({'message': 'Gasto deshecho exitosamente'}, 
                              status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )