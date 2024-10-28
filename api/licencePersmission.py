from rest_framework import permissions
from django.utils import timezone
from .models import License
from rest_framework.exceptions import PermissionDenied

class HasValidLicense(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario tiene una licencia válida y activa
    """

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado
        if not request.user or not request.user.is_authenticated:
            return False
            
        try:
            # Obtener la licencia del usuario
            license = License.objects.get(user=request.user)
            
            # Verificar si la licencia está activa y no ha expirado
            now = timezone.now()
            if not license.active or license.expiration_date <= now:
                raise PermissionDenied("Su licencia ha expirado. Por favor renueve su suscripción.")
                
            return True
                   
        except License.DoesNotExist:
            return False
