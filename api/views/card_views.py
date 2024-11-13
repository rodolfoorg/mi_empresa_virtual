from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Card
from ..serializers import CardSerializer
from ..mixins import BusinessFilterMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

class CardViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = CardSerializer
    queryset = Card.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'business'):
            return Card.objects.none()
        return Card.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'business'):
            raise ValidationError("Usuario no tiene negocio asociado")
        serializer.save(business=self.request.user.business)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
