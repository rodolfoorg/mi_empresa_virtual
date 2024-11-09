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
            
class IsSuperUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a superusuarios para operaciones de escritura
    """
    
    def has_permission(self, request, view):
        # Permitir lectura a cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
            
        # Para operaciones de escritura, verificar si es superusuario
        return bool(request.user and request.user.is_superuser)
