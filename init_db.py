"""Script de inicialización de base de datos.
Crea tablas necesarias tanto para SQLite como para PostgreSQL.
Uso:
  python init_db.py            # Usa DATABASE_URL si existe, sino SQLite local
Variables de entorno:
  DATABASE_URL=<dsn postgres>  # Opcional
  FORCE_RESET=1                # (opcional) eliminar tablas antes de crear (DROP)
"""
from __future__ import annotations
import os, sqlite3, sys, re

HAS_PG = False
try:
    import psycopg2
    HAS_PG = True
except Exception:
    psycopg2 = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'gestor_stock.db')

def is_postgres():
    dsn = os.environ.get('DATABASE_URL')
    return bool(dsn and HAS_PG)

def connect():
    if is_postgres():
        dsn = os.environ['DATABASE_URL']
        if dsn.startswith('postgres://'):
            dsn = dsn.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(dsn)
        try:
            conn.autocommit = True
        except Exception:
            pass
        return conn
    else:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn

# Definiciones de tablas (dialecto neutro con placeholders genéricos '?')
# Ajustes específicos en build_sql.
TABLES = {
    'usuarios': {
        'sql': """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT
        )
        """
    },
    'stock': {
        'sql': """
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            nombre TEXT,
            precio REAL,
            cantidad INTEGER,
            proveedor TEXT,
            observaciones TEXT,
            precio_texto TEXT,
            dueno TEXT,
            fecha_compra TEXT,
            created_at TEXT
        )
        """
    },
    'stock_history': {
        'sql': """
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER,
            codigo TEXT,
            nombre TEXT,
            precio REAL,
            cantidad INTEGER,
            fecha_compra TEXT,
            proveedor TEXT,
            observaciones TEXT,
            precio_texto TEXT,
            dueno TEXT,
            created_at TEXT,
            fecha_evento TEXT,
            tipo_cambio TEXT,
            fuente TEXT,
            usuario TEXT
        )
        """
    },
    'carrito': {
        'sql': """
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            nombre TEXT,
            cantidad INTEGER,
            precio REAL,
            precio_texto TEXT,
            proveedor TEXT,
            avisar_bajo_stock INTEGER DEFAULT 0,
            min_stock_aviso INTEGER,
            dueno TEXT
        )
        """
    },
    'productos_manual': {
        'sql': """
        CREATE TABLE IF NOT EXISTS productos_manual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            nombre TEXT,
            precio REAL,
            proveedor TEXT,
            dueno TEXT,
            observaciones TEXT
        )
        """
    },
    'proveedores_manual': {
        'sql': """
        CREATE TABLE IF NOT EXISTS proveedores_manual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            dueno TEXT,
            activo INTEGER DEFAULT 1
        )
        """
    },
    'proveedores_ocultos': {
        'sql': """
        CREATE TABLE IF NOT EXISTS proveedores_ocultos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            dueno TEXT,
            motivo TEXT,
            created_at TEXT
        )
        """
    }
}

UNIQUE_INDEXES = [
    ("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username)", "usuarios"),
]

def adapt_for_postgres(sql: str) -> str:
    # Remplazos básicos
    sql2 = re.sub(r'INTEGER\\s+PRIMARY\\s+KEY\\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
    return sql2

def maybe_drop(conn):
    if not os.environ.get('FORCE_RESET'):
        return
    cur = conn.cursor()
    print("-- FORCE_RESET=1: Eliminando tablas si existen")
    for tbl in list(TABLES.keys())[::-1]:  # orden inverso por dependencias potenciales
        try:
            if is_postgres():
                cur.execute(f'DROP TABLE IF EXISTS {tbl} CASCADE')
            else:
                cur.execute(f'DROP TABLE IF EXISTS {tbl}')
        except Exception as e:
            print(f"  (warn) No se pudo eliminar {tbl}: {e}")
    cur.close()


def create_tables(conn):
    cur = conn.cursor()
    for name, info in TABLES.items():
        sql = info['sql']
        if is_postgres():
            sql = adapt_for_postgres(sql)
        try:
            cur.execute(sql)
            print(f"Tabla '{name}' OK")
        except Exception as e:
            print(f"Error creando tabla {name}: {e}")
    # Índices / constraints adicionales
    for idx_sql, tbl in UNIQUE_INDEXES:
        try:
            cur.execute(adapt_for_postgres(idx_sql) if is_postgres() else idx_sql)
        except Exception as e:
            print(f"(warn) Índice para {tbl} no creado: {e}")
    cur.close()


def seed_basic(conn):
    """Insertar usuario admin si no existe."""
    cur = conn.cursor()
    try:
        if is_postgres():
            cur.execute("SELECT 1 FROM usuarios WHERE username=%s LIMIT 1", ('admin',))
        else:
            cur.execute("SELECT 1 FROM usuarios WHERE username=? LIMIT 1", ('admin',))
        exists = cur.fetchone()
        if not exists:
            if is_postgres():
                cur.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", ('admin','admin','admin'))
            else:
                cur.execute("INSERT INTO usuarios (username, password, rol) VALUES (?,?,?)", ('admin','admin','admin'))
            if not is_postgres():
                conn.commit()
            print("Usuario admin creado (usuario=admin, password=admin) — cambie la contraseña en producción.")
        else:
            print("Usuario admin ya existe. Sin cambios.")
    except Exception as e:
        print(f"(warn) No se pudo insertar usuario admin: {e}")
    finally:
        cur.close()


def main():
    print("== Inicialización de Base de Datos ==")
    print("Motor:", 'PostgreSQL' if is_postgres() else 'SQLite')
    conn = connect()
    if not conn:
        print("ERROR: No se pudo obtener conexión.")
        sys.exit(1)
    try:
        maybe_drop(conn)
        create_tables(conn)
        seed_basic(conn)
    finally:
        try:
            conn.close()
        except Exception:
            pass
    print("Listo.")

if __name__ == '__main__':
    main()
