#!/usr/bin/env python3
"""
Script simple de migraciones.

Uso:
  python migrate.py status        # Lista migraciones (aplicadas / pendientes)
  python migrate.py apply         # Aplica todas las pendientes en orden
  python migrate.py apply 002     # Aplica solo la versión indicada (si pendiente)
  python migrate.py mark_all      # Marca todas las existentes como aplicadas SIN ejecutar (usar con cuidado)

Convenciones:
  - Carpeta migrations/ con archivos: XXX_descripcion.sql donde XXX es número incremental (ej: 001, 002, 010)
  - Tabla schema_migrations controla versiones aplicadas.
  - Cada archivo puede contener múltiples sentencias separadas por ';'.
  - Se ejecutan dentro de una transacción (si el motor lo soporta) salvo que incluya sentencias no transaccionables.

Compatibilidad:
  - SQLite y PostgreSQL. Detecta DATABASE_URL. Si es postgres:// lo normaliza a postgresql://.

Recomendación:
  - Mantener cada migración idempotente cuando sea posible (usar IF NOT EXISTS, verificar columnas antes de añadir, etc.).
"""
import os, sys, re, datetime, unicodedata
import sqlite3

try:
    import psycopg2  # type: ignore
except Exception:
    psycopg2 = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MIGRATIONS_DIR = os.path.join(BASE_DIR, 'migrations')
DB_SQLITE_PATH = os.path.join(BASE_DIR, 'gestor_stock.sqlite3')

RE_VERSION = re.compile(r'^(\d{3})_.*\.sql$')


def is_postgres():
    url = os.environ.get('DATABASE_URL') or ''
    return 'postgres' in url.lower()


def get_connection():
    if is_postgres():
        if not psycopg2:
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


def ensure_schema_migrations_table(cur):
    if is_postgres():
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def list_migration_files():
    if not os.path.isdir(MIGRATIONS_DIR):
        return []
    files = []
    for fname in os.listdir(MIGRATIONS_DIR):
        if RE_VERSION.match(fname):
            files.append(fname)
    return sorted(files)


def get_applied_versions(cur):
    cur.execute("SELECT version FROM schema_migrations ORDER BY version")
    rows = cur.fetchall()
    return {r[0] if not hasattr(r, 'keys') else r['version'] for r in rows}


def read_sql_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def split_statements(sql):
    # División naive por ';' que no esté dentro de comillas simples o dobles
    statements = []
    current = []
    in_single = False
    in_double = False
    prev = ''
    for ch in sql:
        if ch == "'" and not in_double and prev != '\\':
            in_single = not in_single
        elif ch == '"' and not in_single and prev != '\\':
            in_double = not in_double
        if ch == ';' and not in_single and not in_double:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(ch)
        prev = ch
    tail = ''.join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def apply_migration(cur, version, path):
    sql = read_sql_file(path)
    statements = split_statements(sql)
    if not statements:
        print(f"[WARN] {version}: archivo vacío")
        return
    print(f"[APPLY] {version}: ejecutando {len(statements)} sentencias...")
    for stmt in statements:
        if not stmt:
            continue
        try:
            cur.execute(stmt)
        except Exception as e:
            print(f"[ERROR] Falló sentencia en {version}: {e}\nSQL: {stmt[:400]}")
            raise
    # Registrar versión
    cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)" if is_postgres() else "INSERT INTO schema_migrations (version) VALUES (?)", (version,))


def cmd_status():
    conn = get_connection()
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    applied = get_applied_versions(cur)
    files = list_migration_files()
    if not files:
        print("No hay archivos de migración.")
        return
    print("Versión  | Estado   | Archivo")
    print("---------+----------+----------------------------------")
    for f in files:
        m = RE_VERSION.match(f)
        if not m:
            continue
        version = m.group(1)
        estado = 'APLICADA' if version in applied else 'PENDIENTE'
        print(f"{version}    | {estado:8} | {f}")


def cmd_apply(target_version=None):
    conn = get_connection()
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    applied = get_applied_versions(cur)
    files = list_migration_files()
    to_apply = []
    for f in files:
        version = RE_VERSION.match(f).group(1)
        if version in applied:
            continue
        if target_version and version != target_version:
            continue
        to_apply.append((version, f))
    if not to_apply:
        print("No hay migraciones pendientes" + (f" para versión {target_version}" if target_version else ''))
        return
    try:
        for version, fname in to_apply:
            path = os.path.join(MIGRATIONS_DIR, fname)
            apply_migration(cur, version, path)
        conn.commit()
        print("✅ Migraciones aplicadas correctamente.")
    except Exception:
        conn.rollback()
        print("❌ Error: se hizo ROLLBACK de la transacción.")
        raise


def cmd_mark_all():
    conn = get_connection()
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    applied = get_applied_versions(cur)
    files = list_migration_files()
    nuevas = []
    for f in files:
        version = RE_VERSION.match(f).group(1)
        if version not in applied:
            nuevas.append(version)
    if not nuevas:
        print("No hay versiones nuevas que marcar.")
        return
    for v in nuevas:
        cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)" if is_postgres() else "INSERT INTO schema_migrations (version) VALUES (?)", (v,))
    conn.commit()
    print(f"Marcadas como aplicadas: {', '.join(nuevas)}")


def apply_all_migrations():
    """Aplica todas las migraciones pendientes. Esta función se puede llamar programáticamente."""
    try:
        conn = get_connection()
        if not conn:
            print("[ERROR] No se pudo obtener conexión a la base de datos.")
            return False
            
        cur = conn.cursor()
        
        # Asegurar que existe la tabla de control
        ensure_schema_migrations_table(cur)
        
        # Obtener versiones aplicadas
        aplicadas = get_applied_versions(cur)
        
        # Obtener migraciones disponibles
        disponibles = list_migration_files()
        
        # Filtrar solo las nuevas
        pendientes = [v for v, _ in disponibles if v not in aplicadas]
        pendientes.sort()  # Ordenar para aplicar en secuencia
        
        if not pendientes:
            print("No hay migraciones pendientes que aplicar.")
            return True
            
        print(f"Migraciones pendientes: {', '.join(pendientes)}")
        
        # Aplicar cada migración pendiente en orden
        for version in pendientes:
            # Buscar archivo correspondiente
            for v, path in disponibles:
                if v == version:
                    file_path = path
                    break
            else:
                print(f"[ERROR] No se encontró archivo para versión {version}")
                continue
                
            print(f"Aplicando migración {version}...")
            apply_migration(cur, version, file_path)
            
        conn.commit()
        print("Todas las migraciones pendientes aplicadas con éxito.")
        return True
    except Exception as e:
        print(f"[ERROR] Error al aplicar migraciones automáticamente: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'status':
        cmd_status()
    elif cmd == 'apply':
        if len(sys.argv) == 3:
            cmd_apply(sys.argv[2])
        else:
            cmd_apply()
    elif cmd == 'mark_all':
        cmd_mark_all()
    else:
        print(f"Comando no reconocido: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
