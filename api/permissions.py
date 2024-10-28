from rest_framework import permissions

class IsOwnerOrNoAccess(permissions.BasePermission):
    """
    Permiso personalizado para permitir a cualquiera visualizar el objeto,
    pero solo los propietarios pueden editarlo o eliminarlo.
    """

    def has_object_permission(self, request, view, obj):
        # Permitir GET para todos
        if request.method == 'GET':
            return True
            
        # Para otros métodos (PUT, PATCH, DELETE), verificar si es propietario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'business'):
            return obj.business.user == request.user
        elif hasattr(obj, 'product'):
            return obj.product.business.user == request.user
        else:
            return False

    def has_permission(self, request, view):
        # Para listados, permitir GET a todos, otros métodos solo autenticados
        if request.method == 'GET':
            return True
        return request.user and request.user.is_authenticated