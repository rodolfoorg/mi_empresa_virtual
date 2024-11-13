from rest_framework import permissions
from django.utils import timezone
from .models import License

class HasValidLicenseForPublic(permissions.BasePermission):
    """
    Permiso que filtra productos de negocios con licencias expiradas.
    No requiere autenticación para ver productos públicos.
    """
    def has_permission(self, request, view):
        # Para métodos de solo lectura (GET, HEAD, OPTIONS), permitir acceso
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return False  # Denegar otros métodos

    def has_object_permission(self, request, view, obj):
        # Para métodos de solo lectura (GET, HEAD, OPTIONS), permitir acceso
        if request.method in permissions.SAFE_METHODS:
            # Verificar si el negocio es público y tiene licencia válida
            if hasattr(obj, 'is_public'):
                return obj.is_public
            elif hasattr(obj, 'business'):
                return obj.business.is_public
                
        return False  # Denegar otros métodos

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
                return False
                
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
