# Mi Empresa Virtual API

## Descripción
Mi Empresa Virtual API es una aplicación backend desarrollada con Django Rest Framework que proporciona una interfaz de programación de aplicaciones (API) para gestionar diversos aspectos de una empresa virtual, incluyendo productos, ventas, compras, y más.

## Características
- Gestión de productos
- Registro de ventas
- Control de compras
- Manejo de efectivo y tarjetas
- Administración de contactos
- Gestión de negocios

## Requisitos
- Python 3.11.3
- Django 5.1.2
- Django Rest Framework

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mi-empresa-virtual.git
   cd mi-empresa-virtual
   ```

2. Crea un entorno virtual (fuera del proyecto) y actívalo:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

3. Ve al directorio raíz del proyecto e instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Realiza las migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Crea un superusuario:
   ``` ```bash
   python manage.py createsuperuser
   ```

6. Inicia el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Uso
Accede a la API a través de `http://localhost:8000/api/`. Los endpoints disponibles incluyen:

- `/api/productos/`
- `/api/ventas/`
- `/api/compras/`
- `/api/negocios/`
- `/api/efectivos/`
- `/api/tarjetas/`
- `/api/contactos/`

## Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios propuestos antes de realizar un pull request.

#comandos utiles

#Activar el venv
source venv/Scripts/activate

# Comandos útiles de Django

# Levantar el servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Abrir shell de Django
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic

# Crear una nueva aplicación
python manage.py startapp nombre_de_la_app

# Listar todas las migraciones
python manage.py showmigrations

# Verificar problemas en el proyecto
python manage.py check

# Limpiar la base de datos (genera SQL)
python manage.py sqlflush

# Revertir todas las migraciones de una app
python manage.py migrate nombre_de_la_app zero

# Crear un nuevo proyecto Django
django-admin startproject nombre_del_proyecto

# Ejecutar tests
python manage.py test

# Ver la versión de Django
python -m django --version



