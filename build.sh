#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Eliminar base de datos existente y migraciones
rm -f db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Crear nuevas migraciones y aplicarlas
python manage.py makemigrations
python manage.py migrate

# Crear superusuario solo si no existe
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='rodolfo').exists():
    User.objects.create_superuser(
        'rodolfo',
        'rodolfogroero2@gmail.com',
        'semedesempezcuecicrespalapuerca'
    )
"