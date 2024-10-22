from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'negocios', NegocioViewSet)
router.register(r'compras', CompraViewSet)
router.register(r'efectivos', EfectivoViewSet)
router.register(r'tarjetas', TarjetaViewSet)
router.register(r'contactos', ContactoViewSet)

urlpatterns = [
    path('', api_welcome, name='api-welcome'),
    path('', include(router.urls)),
    path('urls', include(router.urls)),
]
