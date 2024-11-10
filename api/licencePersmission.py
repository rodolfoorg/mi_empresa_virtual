from rest_framework import permissions
from django.utils import timezone
from .models import License

class HasValidLicenseForPublic(permissions.BasePermission):
    """
    Permiso que filtra productos de negocios con licencias expiradas.
    No requiere autenticación para ver productos públicos.
    """
    def has_permission(self, request, view):
        return True  # Permitir acceso inicial

    def has_object_permission(self, request, view, obj):
        try:
            # Obtener el usuario dueño del negocio
            business_owner = obj.business.user if hasattr(obj, 'business') else None
            if not business_owner:
                return False  # Si no tiene negocio asociado, no mostrar
            
            # Verificar si el usuario tiene una licencia
            license = License.objects.filter(user=business_owner).first()
            
            # Si no tiene licencia, no mostrar
            if not license:
                return False
            
            # Verificar si la licencia está vigente
            now = timezone.now()
            return license.expiration_date > now
            
        except (AttributeError, License.DoesNotExist):
            return False  # Si hay cualquier error, no mostrar

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
