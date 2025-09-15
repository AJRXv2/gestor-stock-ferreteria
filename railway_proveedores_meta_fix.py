"""
Script para sincronizar la tabla proveedores_meta con proveedores_duenos en Railway (PostgreSQL).
Este script debe ser desplegado y ejecutado directamente en el entorno de Railway.
"""
import os
import sys
import psycopg2
import psycopg2.extras
import traceback

def log(msg):
    """Registra un mensaje en el log."""
    print(f"[RAILWAY_FIX_META] {msg}")
    sys.stdout.flush()  # Para asegurar que los logs se muestran en tiempo real

def sincronizar_proveedores_meta():
    """Sincroniza la tabla proveedores_meta con proveedores_duenos en Railway (PostgreSQL)."""
    log("=== INICIANDO SINCRONIZACIÓN DE PROVEEDORES_META EN RAILWAY ===")
    
    try:
        # Obtener la URL de la base de datos de PostgreSQL
        DATABASE_URL = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
        
        if not DATABASE_URL:
            log("❌ No se encontró la variable DATABASE_URL")
            return {'success': False, 'error': 'No se encontró DATABASE_URL'}
        
        # Conectarse a la base de datos PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 1. Verificar si existe la tabla proveedores_meta
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'proveedores_meta'
            )
        """)
        meta_exists = cursor.fetchone()[0]
        
        if not meta_exists:
            log("La tabla proveedores_meta no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE proveedores_meta (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    dueno TEXT NOT NULL
                )
            """)
            log("✅ Tabla proveedores_meta creada correctamente")
        else:
            log("Tabla proveedores_meta encontrada. Limpiando datos existentes...")
            cursor.execute("DELETE FROM proveedores_meta")
        
        # 2. Obtener relaciones desde proveedores_duenos
        cursor.execute("""
            SELECT p.id, p.nombre, pd.dueno
            FROM proveedores_manual p
            JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
            ORDER BY p.nombre, pd.dueno
        """)
        
        relaciones = cursor.fetchall()
        
        if not relaciones:
            log("❌ No se encontraron relaciones en proveedores_duenos")
            conn.close()
            return {'success': False, 'error': 'No se encontraron relaciones'}
        
        log(f"📊 Se encontraron {len(relaciones)} relaciones para sincronizar")
        
        # 3. Insertar los datos en proveedores_meta
        for rel in relaciones:
            cursor.execute(
                "INSERT INTO proveedores_meta (nombre, dueno) VALUES (%s, %s)",
                (rel['nombre'], rel['dueno'])
            )
        
        # Confirmar los cambios
        conn.commit()
        
        # 4. Verificar la sincronización
        cursor.execute("SELECT COUNT(*) FROM proveedores_meta")
        meta_count = cursor.fetchone()[0]
        
        log(f"📊 Total de registros en proveedores_meta después de la sincronización: {meta_count}")
        
        # 5. Mostrar algunos ejemplos
        cursor.execute("SELECT nombre, dueno FROM proveedores_meta LIMIT 10")
        ejemplos = cursor.fetchall()
        
        log("Ejemplos de registros en proveedores_meta:")
        for i, ejemplo in enumerate(ejemplos, 1):
            log(f"   {i}. {ejemplo['nombre']} ({ejemplo['dueno']})")
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
        log("=== SINCRONIZACIÓN COMPLETADA EXITOSAMENTE ===")
        log("Ahora los proveedores deberían aparecer correctamente en el formulario de agregar productos.")
        
        return {
            'success': True,
            'total_providers': len(relaciones),
            'meta_records_created': meta_count
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        log(f"❌ Error: {str(e)}")
        log(f"Traza del error: {error_traceback}")
        return {
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }

if __name__ == "__main__":
    resultado = sincronizar_proveedores_meta()
    log(f"Resultado: {resultado}")