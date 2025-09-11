import sys
import os

# Añade la ruta del proyecto al path de Python
path = '/home/ferrecasapauluk/gestor_stock'
if path not in sys.path:
    sys.path.insert(0, path)

# Variables de entorno para producción (PythonAnywhere)
# Puedes editar estos valores también en /var/www/ferrecasapauluk_pythonanywhere_com_wsgi.py
os.environ.setdefault('SECRET_KEY', 'brunokhalessiperrocasatresisletaschacoargentina')
# Si migras a MySQL en PA, define estos valores. Si sigues con SQLite, puedes ignorarlos.
os.environ.setdefault('DB_HOST', 'ferrecasapauluk.mysql.pythonanywhere-services.com')
os.environ.setdefault('DB_USER', 'ferrecasapauluk')
os.environ.setdefault('DB_NAME', 'ferrecasapauluk$default')
os.environ.setdefault('DB_PASS', 'pauluK2005')

# Importa la aplicación Flask
from gestor import app as application