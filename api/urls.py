from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Crear el router
router = DefaultRouter()
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

# Definir las rutas adicionales
urlpatterns = [
    path('', include(router.urls)),  # Incluye las rutas del router
    path('register/', RegisterView.as_view(), name='register'),
    
    # Rutas de autenticación
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # Rutas para operaciones financieras
    path('sales/register_sale/', SaleViewSet.as_view({'post': 'register_sale'}), name='register-sale'),
    path('sales/<int:pk>/undo_sale/', SaleViewSet.as_view({'post': 'undo_sale'}), name='undo-sale'),
    path('purchases/register_purchase/', PurchaseViewSet.as_view({'post': 'register_purchase'}), name='register-purchase'),
    path('purchases/<int:pk>/undo_purchase/', PurchaseViewSet.as_view({'post': 'undo_purchase'}), name='undo-purchase'),
    path('expenses/register_expense/', ExpenseViewSet.as_view({'post': 'register_expense'}), name='register-expense'),
    path('expenses/<int:pk>/undo_expense/', ExpenseViewSet.as_view({'post': 'undo_expense'}), name='undo-expense'),

    # Ruta de bienvenida
    path('', api_welcome, name='api-welcome'),
]