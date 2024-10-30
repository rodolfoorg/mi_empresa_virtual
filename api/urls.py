from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Crear el router
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'businesses', BusinessViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'cards', CardViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'public-products', PublicProductViewSet, basename='public-products')
router.register(r'public-businesses', PublicBusinessViewSet, basename='public-businesses')

# Definir las rutas adicionales
urlpatterns = [
    path('', include(router.urls)),  # Incluye las rutas del router
    path('register/', RegisterView.as_view(), name='register'),
    
    # Rutas de autenticación
    path('auth/login/', CustomAuthToken.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # Ruta de bienvenida (si la necesitas)
    path('', api_welcome, name='api-welcome'),
    path('get-username/', GetUsernameByEmail.as_view(), name='get-username'),
]
