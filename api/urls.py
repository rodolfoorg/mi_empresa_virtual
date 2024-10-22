from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, VentaViewSet, api_welcome

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'ventas', VentaViewSet)

urlpatterns = [
    path('', api_welcome, name='api-welcome'),
    path('', include(router.urls)),
    path('urls', include(router.urls)),
]
