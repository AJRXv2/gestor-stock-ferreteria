#!/usr/bin/env python3
"""
Reimportar historial a tabla stock desde un CSV exportado.

Uso básico (dry-run):
  python reimport_from_csv.py historial_con_id_2025-09-13.csv --dry-run

Importar realmente:
  python reimport_from_csv.py historial.csv --default-dueno ferreteria_general

Opciones:
  --dry-run           No inserta ni actualiza, sólo muestra acciones.
  --force             Inserta aunque exista combinación codigo+proveedor (duplicará entradas).
  --update-existing   Si existe combinación codigo+proveedor, actualiza nombre/precio/cantidad/observaciones.
  --default-dueno X   Dueño a usar si no se puede derivar (default ferreteria_general).
  --encoding ENC      Encoding del CSV (default utf-8).
  --sqlite-file PATH  Ruta específica a la base SQLite (si no, intenta autodetectar).

Compatibilidad Postgres:
  Si existe DATABASE_URL en el entorno, se usa para conectar (requiere psycopg2-binary instalado).

CSV esperado con encabezados (orden flexible):
  ID, FechaCompra, Codigo, Nombre, Proveedor, Precio, Cantidad, Observaciones

Notas:
  - ID se ignora (es para referencia) salvo que quieras usarlo para orden.
  - Precio se normaliza: quita $, puntos de miles y convierte coma decimal.
  - Cantidad se convierte a int (default 0 si vacío).
  - fecha_compra se deja tal cual, y created_at = ahora si no existe.
"""
from __future__ import annotations
import csv
import os
import sys
import argparse
import re
import datetime
import sqlite3
from typing import Optional, Tuple

try:
    import psycopg2  # type: ignore
    HAVE_PG = True
except Exception:
    HAVE_PG = False

PRICE_CLEAN_RE = re.compile(r'[^0-9,.-]')


def parse_price(raw: str) -> float:
    if raw is None:
        return 0.0
    s = str(raw).strip()
    if not s:
        return 0.0
    # Remove currency symbols/spaces
    s = PRICE_CLEAN_RE.sub('', s)
    # If comma used as decimal and dot as thousand -> remove dots then replace comma
    # Heuristic: if s.count(',') == 1 and s.count('.') >= 1 and s.rfind(',') > s.rfind('.'):
    # Simplify: remove thousand separators (.) then replace comma with dot
    s = s.replace('.', '')
    s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

def detect_sqlite_file(explicit: Optional[str]) -> Optional[str]:
    """Detecta la ruta del archivo SQLite a usar.
    Prioridad:
      1) argumento explícito (--sqlite-file)
      2) variable de entorno OVERRIDE_SQLITE (para integraciones externas)
      3) archivos candidatos por orden de preferencia
    """
    if explicit and os.path.exists(explicit):
        return explicit
    override = os.getenv('OVERRIDE_SQLITE')
    if override and os.path.exists(override):
        return override
    candidates = [
        'gestor_stock.sqlite3',
        'gestor_stock.db',
        'stock.db'
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

class DBAdapter:
    def __init__(self, default_dueno: str):
        self.default_dueno = default_dueno
        self.pg = False
        self.conn = None
        self._ensure_connection()
        self._ensure_schema()

    def _ensure_connection(self):
        db_url = os.getenv('DATABASE_URL')
        if db_url and HAVE_PG:
            try:
                self.conn = psycopg2.connect(db_url)
                self.pg = True
                print(f"[INFO] Conectado a Postgres: {db_url}")
                return
            except Exception as e:
                print(f"[WARN] No se pudo conectar a Postgres: {e}. Intentando SQLite.")
        # SQLite fallback
        explicit = os.getenv('OVERRIDE_SQLITE')  # establecido si --sqlite-file
        sqlite_path = detect_sqlite_file(explicit)
        if not sqlite_path:
            raise RuntimeError('No se encontró archivo SQLite (gestor_stock.sqlite3 / gestor_stock.db / stock.db). Use --sqlite-file.')
        self.conn = sqlite3.connect(sqlite_path)
        self.pg = False
        print(f"[INFO] Usando SQLite en: {sqlite_path}")

    def _ensure_schema(self):
        """Asegura que la tabla stock tenga las columnas requeridas.
        Esto permite ejecutar el script sobre una BD antigua sin 'dueno' o 'created_at'."""
        cur = self.conn.cursor()
        try:
            if self.pg:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='stock'")
                cols = {r[0].lower() for r in cur.fetchall()}
                alter_stmts = []
                if 'dueno' not in cols:
                    alter_stmts.append("ALTER TABLE stock ADD COLUMN dueno TEXT")
                if 'precio_texto' not in cols:
                    alter_stmts.append("ALTER TABLE stock ADD COLUMN precio_texto TEXT")
                if 'avisar_bajo_stock' not in cols:
                    alter_stmts.append("ALTER TABLE stock ADD COLUMN avisar_bajo_stock INTEGER DEFAULT 0")
                if 'min_stock_aviso' not in cols:
                    alter_stmts.append("ALTER TABLE stock ADD COLUMN min_stock_aviso INTEGER")
                if 'created_at' not in cols:
                    alter_stmts.append("ALTER TABLE stock ADD COLUMN created_at TEXT")
                for stmt in alter_stmts:
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        print(f"[WARN] No se pudo aplicar migración (Postgres): {e}")
                if alter_stmts:
                    self.conn.commit()
            else:
                cur.execute("PRAGMA table_info(stock)")
                info = cur.fetchall()
                col_names = {c[1].lower() for c in info}
                def alter(sql):
                    try:
                        cur.execute(sql)
                    except Exception as e:
                        print(f"[WARN] Alter fallo: {e}")
                if 'dueno' not in col_names:
                    alter("ALTER TABLE stock ADD COLUMN dueno TEXT")
                if 'precio_texto' not in col_names:
                    alter("ALTER TABLE stock ADD COLUMN precio_texto TEXT")
                if 'avisar_bajo_stock' not in col_names:
                    alter("ALTER TABLE stock ADD COLUMN avisar_bajo_stock INTEGER DEFAULT 0")
                if 'min_stock_aviso' not in col_names:
                    alter("ALTER TABLE stock ADD COLUMN min_stock_aviso INTEGER")
                if 'created_at' not in col_names:
                    alter("ALTER TABLE stock ADD COLUMN created_at TEXT")
                self.conn.commit()
        except Exception as e:
            print(f"[WARN] No se pudo verificar/aplicar esquema: {e}")

    def fetch_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT LOWER(COALESCE(codigo,'')), LOWER(COALESCE(proveedor,'')) FROM stock")
        return { (r[0] or '', r[1] or '') for r in cur.fetchall() }

    def upsert(self, row, opts):
        """Insert or update according to flags.
        row keys: codigo, nombre, precio, cantidad, fecha_compra, proveedor, observaciones, dueno
        """
        codigo_l = (row['codigo'] or '').lower()
        proveedor_l = (row['proveedor'] or '').lower()
        cur = self.conn.cursor()
        # Check existence
        cur.execute("SELECT id FROM stock WHERE LOWER(COALESCE(codigo,''))=? AND LOWER(COALESCE(proveedor,''))=?", (codigo_l, proveedor_l))
        existing = cur.fetchone()
        if existing:
            if opts.update_existing:
                cur.execute("UPDATE stock SET nombre=?, precio=?, cantidad=?, observaciones=? WHERE id=?", (
                    row['nombre'], row['precio'], row['cantidad'], row['observaciones'], existing[0]
                ))
                return 'updated'
            elif opts.force:
                # Insert anyway (duplicate history entry)
                cur.execute("""
                    INSERT INTO stock (codigo, nombre, precio, cantidad, fecha_compra, proveedor, observaciones, precio_texto, dueno, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['codigo'], row['nombre'], row['precio'], row['cantidad'], row['fecha_compra'], row['proveedor'], row['observaciones'], str(row['precio']), row['dueno'], row['created_at']
                ))
                return 'inserted-dup'
            else:
                return 'skipped'
        else:
            cur.execute("""
                INSERT INTO stock (codigo, nombre, precio, cantidad, fecha_compra, proveedor, observaciones, precio_texto, dueno, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['codigo'], row['nombre'], row['precio'], row['cantidad'], row['fecha_compra'], row['proveedor'], row['observaciones'], str(row['precio']), row['dueno'], row['created_at']
            ))
            return 'inserted'

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass


def process_csv(path: str, opts):
    adapter = DBAdapter(opts.default_dueno)
    results = { 'inserted':0, 'updated':0, 'skipped':0, 'inserted-dup':0, 'errors':0 }
    rows_total = 0
    now_iso = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(path, 'r', encoding=opts.encoding, newline='') as f:
        reader = csv.DictReader(f)
        headers = [h.lower() for h in reader.fieldnames] if reader.fieldnames else []
        required = {'fechacompra','codigo','nombre','proveedor','precio','cantidad'}
        missing = [r for r in required if r not in headers]
        if missing:
            print(f"[WARN] Faltan columnas esperadas: {missing}. Procedo pero las filas pueden quedar incompletas.")
        for line in reader:
            rows_total += 1
            try:
                fecha_compra = (line.get('FechaCompra') or line.get('fechacompra') or '').strip() or datetime.datetime.now().strftime('%Y-%m-%d')
                codigo = (line.get('Codigo') or line.get('codigo') or '').strip()
                nombre = (line.get('Nombre') or line.get('nombre') or '').strip()
                proveedor = (line.get('Proveedor') or line.get('proveedor') or '').strip()
                precio_raw = (line.get('Precio') or line.get('precio') or '').strip()
                cantidad_raw = (line.get('Cantidad') or line.get('cantidad') or '').strip()
                observaciones = (line.get('Observaciones') or line.get('observaciones') or '').strip()
                if not codigo or not nombre:
                    raise ValueError('Fila sin codigo o nombre')
                precio = parse_price(precio_raw)
                try:
                    cantidad = int(float(cantidad_raw)) if cantidad_raw else 0
                except ValueError:
                    cantidad = 0
                row = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'precio': precio,
                    'cantidad': cantidad,
                    'fecha_compra': fecha_compra,
                    'proveedor': proveedor,
                    'observaciones': observaciones,
                    'dueno': opts.default_dueno,
                    'created_at': now_iso
                }
                if opts.dry_run:
                    # Simular lógica de upsert
                    # Determine existence real-time (chequeo) sin modificar DB
                    cur = adapter.conn.cursor()
                    cur.execute("SELECT 1 FROM stock WHERE LOWER(COALESCE(codigo,''))=? AND LOWER(COALESCE(proveedor,''))=?", (codigo.lower(), proveedor.lower()))
                    exists = cur.fetchone() is not None
                    if exists:
                        if opts.update_existing:
                            results['updated'] += 1
                        elif opts.force:
                            results['inserted-dup'] += 1
                        else:
                            results['skipped'] += 1
                    else:
                        results['inserted'] += 1
                else:
                    status = adapter.upsert(row, opts)
                    results[status] += 1
            except Exception as e:
                results['errors'] += 1
                print(f"[ERROR] Línea {rows_total}: {e}")
    if not opts.dry_run:
        adapter.commit()
    adapter.close()

    print("\n=== RESUMEN ===")
    print(f"Total filas procesadas: {rows_total}")
    for k in ['inserted','updated','inserted-dup','skipped','errors']:
        print(f"{k}: {results[k]}")
    if opts.dry_run:
        print("(dry-run) No se modificó la base de datos.")
    else:
        print("Cambios aplicados.")


def main():
    parser = argparse.ArgumentParser(description='Reimportar historial desde CSV a stock')
    parser.add_argument('csv_path', help='Ruta al archivo CSV exportado')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--update-existing', action='store_true', dest='update_existing')
    parser.add_argument('--default-dueno', default='ferreteria_general')
    parser.add_argument('--encoding', default='utf-8')
    parser.add_argument('--sqlite-file', dest='sqlite_file')
    opts = parser.parse_args()

    if not os.path.exists(opts.csv_path):
        print(f"Archivo CSV no encontrado: {opts.csv_path}")
        sys.exit(1)

    # Override detection if provided
    if opts.sqlite_file:
        if not os.path.exists(opts.sqlite_file):
            print(f"SQLite file no existe: {opts.sqlite_file}")
            sys.exit(1)
        os.environ['OVERRIDE_SQLITE'] = opts.sqlite_file

    process_csv(opts.csv_path, opts)

if __name__ == '__main__':
    main()
