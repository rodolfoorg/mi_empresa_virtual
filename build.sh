#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
# Crear nuevas migraciones y aplicarlas
python manage.py makemigrations
python manage.py migrate

# Crear superusuario solo si no existe
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        'admin',
        'admin@gmail.com',
        '@dmin123*'
    )
"
