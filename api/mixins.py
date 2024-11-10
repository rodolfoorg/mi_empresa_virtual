from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Business

class BusinessFilterMixin:
    """
    Mixin para filtrar automáticamente los objetos por el negocio del usuario autenticado
    """
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Usuario no autenticado")
            
        try:
            business = user.business
        except Business.DoesNotExist:
            raise PermissionDenied("Usuario no tiene un negocio asociado")
            
        queryset = super().get_queryset()
        return queryset.filter(business=business)

    def perform_create(self, serializer):
        user = self.request.user
        try:
            user_business = user.business
            serializer.save(business=user_business)
        except Business.DoesNotExist:
            raise ValidationError({
                "detail": "No business found for current user",
                "user_id": user.id,
                "has_business": False
            })

    def perform_update(self, serializer):
        user = self.request.user
        try:
            user_business = user.business
            serializer.save(business=user_business)
        except Business.DoesNotExist:
            raise ValidationError({
                "detail": "No business found for current user",
                "user_id": user.id,
                "has_business": False
            })