from rest_framework.decorators import api_view
from rest_framework.response import Response
from .financial_views import CardViewSet, ExpenseViewSet
from .user_views import UserViewSet
from .auth_views import AuthViewSet, CustomAuthToken
from .license_views import LicenseViewSet, LicenseRenewalViewSet
from .transaction_views import SaleViewSet, PurchaseViewSet
from .business_views import BusinessViewSet
from .product_views import ProductViewSet
from .contact_views import ContactViewSet
from .public_views import PublicProductViewSet, PublicBusinessViewSet

@api_view(['GET'])
def api_welcome(request):
    return Response({
        "message": "Bienvenido a la API de Mi Empresa Virtual",
        "version": "1.0",
        "endpoints": {
            "api/": "Lista de endpoints disponibles",
            "api/login/": "Autenticación",
            "api/logout/": "Cerrar sesión"
        }
    })

__all__ = [
    'AuthViewSet',
    'CustomAuthToken',
    'api_welcome',
    'BusinessViewSet',
    'PublicBusinessViewSet',
    'ProductViewSet',
    'PublicProductViewSet',
    'SaleViewSet',
    'PurchaseViewSet',
    'CardViewSet',
    'ExpenseViewSet',
    'ContactViewSet',
    'LicenseViewSet',
    'LicenseRenewalViewSet',
    'UserViewSet',
]