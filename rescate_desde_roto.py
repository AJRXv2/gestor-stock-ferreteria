#!/usr/bin/env python3
"""Reconstruye un CSV estándar (rescate_desde_roto.csv) a partir de una base potencialmente rota
   donde 'proveedor' quedó con valores tipo '$0,00' y 'nombre' contiene el proveedor real.

Genera: rescate_desde_roto.csv (NO modifica la base de datos)

Columnas objetivo CSV:
  FechaCompra,Codigo,Nombre,Proveedor,Precio,Cantidad,Observaciones

Heurística aplicada:
  - Si proveedor parece un precio (regex) y nombre coincide con un proveedor conocido, se asume corrimiento:
      codigo -> Nombre real
      nombre -> Proveedor real
      proveedor -> Precio textual original
      precio -> Precio numérico parcialmente parseado (se re-calcula desde texto si es posible)
      cantidad -> 0 (perdida)
  - Caso contrario, se toma la fila tal cual.

Limitaciones:
  - Si el código original se perdió (porque era realmente un nombre), no se puede diferenciar.
  - Los precios con miles se normalizan quitando puntos y usando punto decimal.
  - Cantidades originales no pueden recuperarse si quedaron en 0.

Uso:
  python rescate_desde_roto.py [--db gestor_stock.db] [--out rescate_desde_roto.csv]
"""
import csv, re, argparse, os, sqlite3, sys
from datetime import datetime

PROVEEDORES_CONOCIDOS = {
    'crossmaster','berger','chiesa','cachan','brementools',
    'sorbalok','dewalt','sica','nortedist','otros proveedores'
}

RE_PRECIO = re.compile(r"^\$?\d{1,3}([\.,]\d{3})*(,[0-9]{2})?$")


def parece_precio_txt(v: str) -> bool:
    if v is None:
        return False
    v = str(v).strip()
    if not v:
        return False
    return v.startswith('$') or bool(RE_PRECIO.fullmatch(v))


def normalizar_precio(txt: str) -> float:
    if not txt:
        return 0.0
    t = txt.replace('$','').replace(' ','').strip()
    # si formato miles con puntos y decimales con coma => quitar puntos y coma->.
    t = t.replace('.', '').replace(',', '.')
    try:
        return float(t)
    except Exception:
        return 0.0


def rescatar(db_path: str, out_csv: str):
    if not os.path.exists(db_path):
        print(f"[ERROR] No existe BD: {db_path}")
        return 1
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute('SELECT id,codigo,nombre,proveedor,precio,cantidad,observaciones,precio_texto,fecha_compra FROM stock ORDER BY id').fetchall()
    total = len(rows)
    reparadas = 0
    resultado = []

    for (id_, codigo, nombre, proveedor, precio, cantidad, obs, precio_texto, fecha) in rows:
        fecha = fecha or ''
        codigo_val = codigo or ''
        nombre_val = nombre or ''
        proveedor_val = proveedor or ''
        obs_val = obs or ''
        # Detectar fila rota: proveedor parece precio, nombre es proveedor real
        if parece_precio_txt(proveedor_val) and nombre_val.lower() in PROVEEDORES_CONOCIDOS:
            reparadas += 1
            proveedor_real = nombre_val
            nombre_real = codigo_val  # lo que antes estaba en codigo
            precio_float = normalizar_precio(proveedor_val) if proveedor_val else (precio or 0.0)
            # Cantidad se perdió -> 0
            resultado.append((fecha, '', nombre_real, proveedor_real, precio_float, 0, obs_val))
        else:
            # Fila se considera correcta
            precio_float = float(precio) if isinstance(precio, (int,float)) else normalizar_precio(str(precio or ''))
            cant_int = int(cantidad) if isinstance(cantidad, (int,float)) else 0
            resultado.append((fecha, codigo_val, nombre_val, proveedor_val, precio_float, cant_int, obs_val))

    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['FechaCompra','Codigo','Nombre','Proveedor','Precio','Cantidad','Observaciones'])
        w.writerows(resultado)

    print(f"[OK] Generado {out_csv} con {len(resultado)} filas.")
    print(f"[INFO] Filas detectadas como rotas y reparadas: {reparadas} / {total}")
    print("[NOTA] Revise manualmente varias filas antes de reimportar.")
    conn.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description='Rescate de filas desalineadas en stock')
    parser.add_argument('--db', default='gestor_stock.db', help='Ruta BD origen')
    parser.add_argument('--out', default='rescate_desde_roto.csv', help='Archivo CSV salida')
    args = parser.parse_args()
    sys.exit(rescatar(args.db, args.out))

if __name__ == '__main__':
    main()
