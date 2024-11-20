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
    BusinessSettingsViewSet,
    PublicBusinessSettingsViewSet,
    CustomAuthToken,
    api_welcome,
    OrderViewSet
)

router = DefaultRouter()

# ViewSets que necesitan basename porque usan get_queryset()

router.register(r'business-settings', BusinessSettingsViewSet, basename='business-settings')
router.register(r'business-settings/(?P<business_id>\d+)/public', PublicBusinessSettingsViewSet, basename='public-business-settings')

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

urlpatterns = [
    path('', api_welcome),
    path('', include(router.urls)),
    path('token-auth/', CustomAuthToken.as_view()),
]