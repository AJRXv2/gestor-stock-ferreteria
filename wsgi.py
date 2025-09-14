import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno de .env si existe
load_dotenv()

# Añadir el directorio actual al path si no está ya
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Variables de entorno para desarrollo local (serán sobrescritas por las de Railway en producción)
if not os.environ.get('SECRET_KEY'):
    os.environ.setdefault('SECRET_KEY', 'brunokhalessiperrocasatresisletaschacoargentina')

# Ejecutar migraciones de base de datos
print("Ejecutando migraciones de base de datos...")
try:
    import migrate
    success = migrate.apply_all_migrations()
    if success:
        print("Migraciones aplicadas con éxito")
    else:
        print("Advertencia: Algunas migraciones no se aplicaron correctamente")
except Exception as e:
    print(f"Error al aplicar migraciones: {e}")
    print("Continuando con la inicialización de la aplicación de todos modos...")

# En Railway, DATABASE_URL se configura automáticamente cuando agregas una base de datos PostgreSQL

# Importa la aplicación Flask
from gestor import app as application