import os
import sys

from mi_empresa_virtual.wsgi import application

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__)) 