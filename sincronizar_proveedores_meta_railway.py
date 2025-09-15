"""
Script para sincronizar proveedores_meta con proveedores_duenos en la base de datos PostgreSQL de Railway.
"""
import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_railway_connection():
    """Obtiene la conexión a la base de datos PostgreSQL de Railway."""
    try:
        # Verificar si tenemos la URL de la base de datos como variable de entorno
        database_url = os.environ.get('DATABASE_URL')
        
        # Solicitar la URL si no está disponible
        if not database_url:
            print("\n🔄 No se encontró la URL de la base de datos de Railway en las variables de entorno.")
            database_url = input("Ingresa la URL de la base de datos de Railway (postgresql://...): ")
            
            if not database_url:
                print("❌ No se proporcionó URL de base de datos.")
                return None
            
            # Establecer como variable de entorno para futuras referencias
            os.environ['DATABASE_URL'] = database_url
        
        # Asegurar que el formato de la URL sea correcto
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"🔌 Conectando a Railway PostgreSQL: {database_url.split('@')[1] if '@' in database_url else '***OCULTO***'}")
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Error al conectar con Railway: {e}")
        return None

def db_query_railway(query, params=(), fetch=False):
    """Ejecuta una consulta en la base de datos PostgreSQL de Railway."""
    conn = get_railway_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en consulta PostgreSQL: {query}  \nParams: {params}\nError: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()

def sincronizar_proveedores_meta_railway():
    """Sincroniza proveedores_meta con los datos de proveedores_duenos en Railway."""
    print("\n=== SINCRONIZAR PROVEEDORES_META CON PROVEEDORES_DUENOS EN RAILWAY ===\n")
    
    # 1. Verificar si existe la tabla proveedores_meta
    try:
        meta_exists = db_query_railway("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'proveedores_meta'
            ) as exists
        """, fetch=True)
        
        if not meta_exists or not meta_exists[0]['exists']:
            print("La tabla proveedores_meta no existe en Railway. Creándola...")
            db_query_railway("""
                CREATE TABLE proveedores_meta (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    dueno TEXT NOT NULL
                )
            """)
            print("✅ Tabla proveedores_meta creada correctamente en Railway.")
        else:
            print("Tabla proveedores_meta encontrada en Railway.")
            
            # Limpiar tabla existente
            db_query_railway("DELETE FROM proveedores_meta")
            print("Tabla proveedores_meta limpiada para actualización.")
    except Exception as e:
        print(f"Error al verificar/crear tabla proveedores_meta en Railway: {e}")
        return
    
    # 2. Obtener los datos de proveedores_duenos
    relaciones = db_query_railway("""
        SELECT p.id, p.nombre, pd.dueno
        FROM proveedores_manual p
        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        ORDER BY p.nombre, pd.dueno
    """, fetch=True)
    
    if not relaciones:
        print("❌ No se encontraron relaciones en proveedores_duenos en Railway.")
        return
    
    print(f"Se encontraron {len(relaciones)} relaciones para sincronizar en Railway.")
    
    # 3. Insertar los datos en proveedores_meta
    for rel in relaciones:
        result = db_query_railway(
            "INSERT INTO proveedores_meta (nombre, dueno) VALUES (%s, %s)",
            (rel['nombre'], rel['dueno'])
        )
        if not result:
            print(f"❌ Error al insertar relación para {rel['nombre']} ({rel['dueno']}).")
    
    # 4. Verificar la sincronización
    meta_count = db_query_railway("SELECT COUNT(*) as count FROM proveedores_meta", fetch=True)[0]['count']
    print(f"\nTotal de registros en proveedores_meta después de la sincronización: {meta_count}")
    
    # Listar algunos ejemplos
    ejemplos = db_query_railway("SELECT nombre, dueno FROM proveedores_meta LIMIT 10", fetch=True)
    print("\nEjemplos de registros en proveedores_meta en Railway:")
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"   {i}. {ejemplo['nombre']} ({ejemplo['dueno']})")
    
    print("\n=== SINCRONIZACIÓN EN RAILWAY COMPLETADA ===\n")
    print("✅ La tabla proveedores_meta en Railway ha sido actualizada con los datos de proveedores_duenos.")
    print("Ahora el formulario de agregar productos debería mostrar correctamente los proveedores en la versión online.")

if __name__ == "__main__":
    sincronizar_proveedores_meta_railway()