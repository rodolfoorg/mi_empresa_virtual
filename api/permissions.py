from rest_framework import permissions

class IsOwnerOrNoAccess(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los propietarios de un objeto
    visualizarlo, editarlo o eliminarlo.
    """

    def has_object_permission(self, request, view, obj):
        # Verificar si el usuario es el propietario del objeto
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'business'):
            return obj.business.user == request.user
        elif hasattr(obj, 'product'):
            return obj.product.business.user == request.user
        else:
            return False

    def has_permission(self, request, view):
        # Para listados, permitir solo si el usuario está autenticado
        return request.user and request.user.is_authenticated