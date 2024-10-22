"""
URL configuration for mi_empresa_virtual project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import api_welcome, CustomAuthToken, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_welcome, name='home'),  # Usa api_welcome directamente en la raíz
    path('api/', include('api.urls')),  # Mantén las otras rutas de la API bajo /api/
    path('api/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
]
