from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'businesses', BusinessViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'cash', CashViewSet)
router.register(r'cards', CardViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'licenses', LicenseViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
