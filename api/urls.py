from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Crear el router
router = DefaultRouter()

# Registrar todas las rutas
router.register(r'products', ProductViewSet)
router.register(r'user', UserViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'businesses', BusinessViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'cards', CardViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'public-products', PublicProductViewSet, basename='public-products')
router.register(r'public-businesses', PublicBusinessViewSet, basename='public-businesses')
router.register(r'auth', AuthViewSet, basename='auth')  # Nueva vista para autenticación

# Definir las rutas
urlpatterns = [
    path('', include(router.urls)),
]