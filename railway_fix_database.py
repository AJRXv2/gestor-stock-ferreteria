import os
import psycopg2
from urllib.parse import urlparse

def execute_migration():
    # Obtener la URL de la base de datos desde las variables de entorno
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("[ERROR] No se encontró la variable de entorno DATABASE_URL")
        return False
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Leer el script SQL
        with open('railway_fix_database.sql', 'r') as f:
            sql_script = f.read()
        
        # Ejecutar el script
        cur.execute(sql_script)
        
        # Commit y cerrar
        conn.commit()
        cur.close()
        conn.close()
        
        print("[SUCCESS] Migración aplicada correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error al aplicar la migración: {e}")
        return False

if __name__ == "__main__":
    execute_migration()
