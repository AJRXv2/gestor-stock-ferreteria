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
    try:
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
        print("[INFO] Tabla schema_migrations verificada o creada")
    except Exception as e:
        print(f"[ERROR] Error al crear tabla schema_migrations: {e}")
        raise


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
    # División por ';' que no esté dentro de comillas simples o dobles
    # También ignora comentarios de línea (--) y bloques de comentarios (/* */)
    statements = []
    current = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    prev = ''
    
    lines = sql.split('\n')
    for line in lines:
        line = line.strip()
        # Ignorar líneas de comentario completas
        if line.startswith('--'):
            continue
            
        for i, ch in enumerate(line):
            # Detectar inicio de comentario de línea
            if ch == '-' and i+1 < len(line) and line[i+1] == '-' and not in_single and not in_double and not in_block_comment:
                in_line_comment = True
                continue
                
            # Ignorar todo dentro de un comentario de línea
            if in_line_comment:
                continue
                
            # Detectar inicio de bloque de comentario
            if ch == '/' and i+1 < len(line) and line[i+1] == '*' and not in_single and not in_double:
                in_block_comment = True
                prev = ch
                continue
                
            # Detectar fin de bloque de comentario
            if ch == '/' and prev == '*' and in_block_comment:
                in_block_comment = False
                prev = ch
                continue
                
            # Ignorar todo dentro de un bloque de comentario
            if in_block_comment:
                prev = ch
                continue
                
            # Manejar comillas
            if ch == "'" and not in_double and prev != '\\':
                in_single = not in_single
            elif ch == '"' and not in_single and prev != '\\':
                in_double = not in_double
                
            # Detectar fin de sentencia
            if ch == ';' and not in_single and not in_double:
                stmt = ''.join(current).strip()
                if stmt:  # Solo agregar si no está vacío
                    statements.append(stmt)
                current = []
            else:
                current.append(ch)
            prev = ch
        
        # Reiniciar estado de comentario de línea al final de cada línea
        in_line_comment = False
        
        # Agregar salto de línea si no estamos en un comentario
        if not in_block_comment and current:
            current.append('\n')
    
    # Agregar la última sentencia si existe
    tail = ''.join(current).strip()
    if tail:
        statements.append(tail)
        
    # Filtrar sentencias vacías o que solo contienen espacios en blanco
    return [stmt for stmt in statements if stmt.strip()]


def adapt_sql_for_postgres(sql):
    """Adaptar sintaxis SQLite a PostgreSQL."""
    # Si la sentencia está vacía, devolver vacío
    if not sql or sql.isspace():
        return ""
        
    # Ignorar comandos específicos de SQLite
    if sql.strip().upper().startswith("PRAGMA"):
        return ""
        
    # Reemplazar AUTOINCREMENT por SERIAL
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    
    # Reemplazar IF NOT EXISTS para columnas (sintaxis específica de SQLite)
    if "COMMENT ON TABLE IF EXISTS" in sql:
        # PostgreSQL soporta COMMENT ON TABLE pero no el IF EXISTS
        sql = sql.replace("COMMENT ON TABLE IF EXISTS", "COMMENT ON TABLE")
    
    # Ignorar o adaptar comandos específicos de algún motor
    if sql.strip().upper().startswith("SELECT 'VERIFICANDO"):
        # Es un comando de diagnóstico, mantenerlo
        return sql
        
    # Otros reemplazos que puedan ser necesarios
    return sql

def adapt_sql_for_sqlite(sql):
    """Adaptar sintaxis PostgreSQL a SQLite."""
    # Si la sentencia está vacía, devolver vacío
    if not sql or sql.isspace():
        return ""
        
    # Ignorar sentencias específicas de PostgreSQL
    if "ALTER TABLE" in sql and "ADD COLUMN IF NOT EXISTS" in sql:
        # SQLite no soporta IF NOT EXISTS en ADD COLUMN
        return ""
        
    # Ignorar comandos de diagnóstico
    if sql.strip().upper().startswith("SELECT 'VERIFICANDO"):
        return ""
        
    # Ignorar bloques PL/pgSQL
    if sql.strip().startswith("DO $$"):
        return ""
        
    return sql


def apply_migration(cur, version, path):
    sql = read_sql_file(path)
    statements = split_statements(sql)
    if not statements:
        print(f"[WARN] {version}: archivo vacío o solo contiene comentarios")
        return
    
    print(f"[APPLY] {version}: ejecutando {len(statements)} sentencias...")
    count = 0
    for stmt in statements:
        if not stmt or stmt.isspace():
            continue
            
        try:
            # Adaptar SQL según el motor de base de datos
            if is_postgres():
                stmt = adapt_sql_for_postgres(stmt)
            else:
                stmt = adapt_sql_for_sqlite(stmt)
                
            # Si después de la adaptación la sentencia está vacía, saltarla
            if not stmt or stmt.isspace():
                continue
                
            cur.execute(stmt)
            count += 1
        except Exception as e:
            print(f"[ERROR] Falló sentencia en {version}: {e}")
            print(f"SQL: {stmt[:400]}")
            raise
    
    print(f"[INFO] {version}: {count} sentencias ejecutadas correctamente")
    
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
        
        # Obtener migraciones disponibles (archivos)
        archivos = list_migration_files()
        
        # Convertir archivos a versiones y crear mapeo
        versiones_disponibles = []
        mapeo_archivo_ruta = {}
        
        for archivo in archivos:
            match = RE_VERSION.match(archivo)
            if match:
                version = match.group(1)
                versiones_disponibles.append(version)
                mapeo_archivo_ruta[version] = os.path.join(MIGRATIONS_DIR, archivo)
        
        # Filtrar solo las nuevas
        pendientes = [v for v in versiones_disponibles if v not in aplicadas]
        pendientes.sort()  # Ordenar para aplicar en secuencia
        
        if not pendientes:
            print("No hay migraciones pendientes que aplicar.")
            return True
            
        print(f"Migraciones pendientes: {', '.join(pendientes)}")
        
        # Aplicar cada migración pendiente en orden
        exitosos = []
        for version in pendientes:
            try:
                file_path = mapeo_archivo_ruta[version]
                print(f"Aplicando migración {version} desde {file_path}...")
                apply_migration(cur, version, file_path)
                exitosos.append(version)
            except Exception as e:
                # Si falla una migración, hacemos rollback y continuamos con la siguiente
                conn.rollback()
                print(f"[ERROR] Error al aplicar migración {version}: {e}")
                print(f"Se continuará con las siguientes migraciones...")
                continue
        
        if exitosos:
            conn.commit()
            print(f"Migraciones aplicadas con éxito: {', '.join(exitosos)}")
            
        # Informar del estado final
        if len(exitosos) == len(pendientes):
            print("Todas las migraciones pendientes aplicadas con éxito.")
            return True
        else:
            print(f"ADVERTENCIA: Solo se aplicaron {len(exitosos)} de {len(pendientes)} migraciones pendientes.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error al aplicar migraciones automáticamente: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


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
