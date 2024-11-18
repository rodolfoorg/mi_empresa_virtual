from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusinessViewSet,
    PublicBusinessViewSet,
    ProductViewSet,
    PublicProductViewSet,
    OrderViewSet,
    LicenseViewSet,
    BusinessSettingsViewSet,
    PublicBusinessSettingsViewSet,
    CustomAuthToken,
    api_welcome
)

router = DefaultRouter()

# ViewSets que necesitan basename porque usan get_queryset()
router.register(r'public-businesses', PublicBusinessViewSet, basename='public-business')
router.register(r'public-products', PublicProductViewSet, basename='public-product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'business-settings', BusinessSettingsViewSet, basename='business-settings')
router.register(r'business-settings/(?P<business_id>\d+)/public', PublicBusinessSettingsViewSet, basename='public-business-settings')

# ViewSets que tienen queryset estático
router.register(r'businesses', BusinessViewSet)
router.register(r'products', ProductViewSet)
router.register(r'licenses', LicenseViewSet)

urlpatterns = [
    path('', api_welcome),
    path('', include(router.urls)),
    path('token-auth/', CustomAuthToken.as_view()),
]