from rest_framework import permissions
from django.utils import timezone
from .models import License
from rest_framework.exceptions import PermissionDenied

class HasValidLicenseForPublic(permissions.BasePermission):
    """
    Permiso que verifica si la licencia está activa para ver contenido público.
    No permite ver contenido público si la licencia está expirada.
    """
    def has_permission(self, request, view):
        # Si el usuario no está autenticado, no tiene acceso
        if not request.user or not request.user.is_authenticated:
            return False
            
        try:
            license = License.objects.get(user=request.user)
            now = timezone.now()
            
            # Si la licencia está expirada, no permitir acceso
            if license.expiration_date <= now:
                raise PermissionDenied(
                    "Su licencia ha expirado. Por favor renueve su suscripción para ver contenido público."
                )
                
            return True
            
        except License.DoesNotExist:
            return False

class HasValidLicenseForReadOnly(permissions.BasePermission):
    """
    Permiso que permite solo lectura si la licencia está expirada.
    No permite operaciones de escritura con licencia expirada.
    """
    def has_permission(self, request, view):
        # Si el usuario no está autenticado, no tiene acceso
        if not request.user or not request.user.is_authenticated:
            return False
            
        try:
            license = License.objects.get(user=request.user)
            now = timezone.now()
            
            # Si es una operación de lectura, permitir siempre
            if request.method in permissions.SAFE_METHODS:
                return True
                
            # Para operaciones de escritura, verificar si la licencia está vigente
            if license.expiration_date <= now:
                raise PermissionDenied(
                    "Su licencia ha expirado. Por favor renueve su suscripción para realizar esta operación."
                )
                
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
