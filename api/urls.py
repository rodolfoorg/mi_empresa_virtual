from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CardViewSet,
    ExpenseViewSet,
    ContactViewSet,
    LicenseViewSet,
    LicenseRenewalViewSet,
    UserViewSet,
    ProductViewSet,
    SaleViewSet,
    BusinessViewSet,
    PurchaseViewSet,
    PublicBusinessViewSet,
    PublicProductViewSet,
    AuthViewSet,
    public_views,
)
from .views.order_views import OrderViewSet
from .views.user_views import UserProfileView

# Crear el router
router = DefaultRouter()

# Registrar todas las rutas
router.register(r'products', ProductViewSet)
router.register(r'public-products', PublicProductViewSet, basename='public-products')
router.register(r'user', UserViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'purchases', PurchaseViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'cards', CardViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'public-businesses', PublicBusinessViewSet, basename='public-businesses')
router.register(r'auth', AuthViewSet, basename='auth')  # Nueva vista para autenticación
router.register(r'license-renewals', LicenseRenewalViewSet)
router.register(r'orders', OrderViewSet, basename='order')

# Definir las rutas
urlpatterns = [
    path('', include(router.urls)),
    path('orders/track/<str:tracking_code>/', 
         public_views.track_order, 
         name='track-order'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
]