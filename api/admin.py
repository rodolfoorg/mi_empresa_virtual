from django.contrib import admin
from django.apps import apps

# Obtén el modelo de la aplicación
app_models = apps.get_app_config('api').get_models()

# Registra cada modelo en el admin
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass