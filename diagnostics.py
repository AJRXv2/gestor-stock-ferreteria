import os
import sys
import json
import sqlite3
import traceback

# Importar psycopg2 si está disponible
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# Ruta a la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SQLITE_PATH = os.path.join(BASE_DIR, os.getenv('DATABASE_FILE', 'gestor_stock.db'))

def is_postgres():
    """Determinar si se usa PostgreSQL basado en variable de entorno DATABASE_URL."""
    url = os.environ.get('DATABASE_URL', '')
    return 'postgres' in url.lower()

def get_connection():
    """Obtener conexión a la base de datos (PostgreSQL o SQLite)."""
    if is_postgres():
        if not HAS_POSTGRES:
            print("[ERROR] psycopg2-binary no instalado para PostgreSQL")
            sys.exit(1)
        dsn = os.environ.get('DATABASE_URL')
        if dsn.startswith('postgres://'):
            dsn = 'postgresql://' + dsn[len('postgres://'):]
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
        return conn
    else:
        return sqlite3.connect(DB_SQLITE_PATH)

def get_table_info_sqlite(conn, table_name):
    """Obtener información de columnas de una tabla en SQLite."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return [{'name': col[1], 'type': col[2]} for col in columns]

def get_table_info_postgres(conn, table_name):
    """Obtener información de columnas de una tabla en PostgreSQL."""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
    """)
    columns = cursor.fetchall()
    return [{'name': col[0], 'type': col[1]} for col in columns]

def get_table_info(conn, table_name):
    """Obtener información de columnas de una tabla."""
    if is_postgres():
        return get_table_info_postgres(conn, table_name)
    else:
        return get_table_info_sqlite(conn, table_name)

def check_and_repair_columns(conn, table_name, required_columns):
    """Verificar y reparar columnas faltantes en una tabla."""
    cursor = conn.cursor()
    
    # Obtener columnas existentes
    existing_columns = get_table_info(conn, table_name)
    existing_column_names = [col['name'] for col in existing_columns]
    
    # Verificar columnas faltantes
    missing_columns = []
    for col_name, col_type in required_columns.items():
        if col_name not in existing_column_names:
            missing_columns.append((col_name, col_type))
    
    # Agregar columnas faltantes
    if missing_columns:
        print(f"[REPAIR] Agregando columnas faltantes a {table_name}: {', '.join(c[0] for c in missing_columns)}")
        for col_name, col_type in missing_columns:
            try:
                if is_postgres():
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                else:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                print(f"[REPAIR] Columna {col_name} agregada a {table_name}")
            except Exception as e:
                print(f"[ERROR] No se pudo agregar columna {col_name} a {table_name}: {e}")
    else:
        print(f"[OK] Tabla {table_name} tiene todas las columnas requeridas")
    
    conn.commit()

def run_diagnostics():
    """Ejecutar diagnóstico completo de la base de datos."""
    print("=== DIAGNÓSTICO DE BASE DE DATOS ===")
    print(f"Motor: {'PostgreSQL' if is_postgres() else 'SQLite'}")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que existen todas las tablas necesarias
        required_tables = [
            'usuarios', 'stock', 'stock_history', 'carrito', 
            'productos_manual', 'proveedores_manual', 
            'proveedores_ocultos', 'schema_migrations',
            'proveedores_duenos'
        ]
        
        # Listar todas las tablas
        if is_postgres():
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Tablas encontradas: {', '.join(existing_tables)}")
        
        # Verificar tablas faltantes
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            print(f"[ERROR] Tablas faltantes: {', '.join(missing_tables)}")
        else:
            print("[OK] Todas las tablas requeridas existen")
        
        # Verificar y reparar columnas en las tablas existentes
        if 'productos_manual' in existing_tables:
            check_and_repair_columns(conn, 'productos_manual', {
                'id': 'INTEGER PRIMARY KEY' if not is_postgres() else 'SERIAL PRIMARY KEY',
                'nombre': 'TEXT NOT NULL',
                'codigo': 'TEXT',
                'precio': 'REAL DEFAULT 0',
                'proveedor': 'TEXT',
                'observaciones': 'TEXT',
                'dueno': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })
        
        if 'proveedores_manual' in existing_tables:
            check_and_repair_columns(conn, 'proveedores_manual', {
                'id': 'INTEGER PRIMARY KEY' if not is_postgres() else 'SERIAL PRIMARY KEY',
                'nombre': 'TEXT NOT NULL',
                'oculto': 'INTEGER DEFAULT 0',
                'dueno': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })
        
        if 'stock' in existing_tables:
            check_and_repair_columns(conn, 'stock', {
                'dueno': 'TEXT',
                'avisar_bajo_stock': 'INTEGER DEFAULT 0',
                'min_stock_aviso': 'INTEGER'
            })
        
        # Verificar si existen los índices necesarios
        if is_postgres():
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'productos_manual' AND indexname = 'idx_prodmanual_dueno'
            """)
            if not cursor.fetchone():
                print("[REPAIR] Creando índice idx_prodmanual_dueno en productos_manual")
                try:
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prodmanual_dueno ON productos_manual(LOWER(dueno))")
                    print("[OK] Índice idx_prodmanual_dueno creado")
                except Exception as e:
                    print(f"[ERROR] No se pudo crear el índice idx_prodmanual_dueno: {e}")
        
        # Commit de los cambios
        conn.commit()
        
        print("=== DIAGNÓSTICO COMPLETADO ===")
    
    except Exception as e:
        print(f"[ERROR] Error durante el diagnóstico: {e}")
        traceback.print_exc()
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    run_diagnostics()