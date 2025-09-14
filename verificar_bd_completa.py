import sqlite3
import os
import json

# Función para conectar a la base de datos
def conectar_bd(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Función para ejecutar consultas
def ejecutar_consulta(conn, query, params=None):
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")
        return []

# Función para mostrar resultados de manera legible
def mostrar_resultados(resultados, titulo):
    print(f"\n===== {titulo} =====")
    if not resultados:
        print("No se encontraron resultados")
        return
    
    print(f"Se encontraron {len(resultados)} resultados:")
    for i, row in enumerate(resultados, 1):
        print(f"Resultado {i}:")
        row_dict = {k: row[k] for k in row.keys()}
        print(json.dumps(row_dict, indent=2, ensure_ascii=False))

# Rutas de las bases de datos
db_paths = [
    "gestor_stock.db",
    "gestor_stock.sqlite3",
    "stock.db"
]

# Buscar el producto TERM32A y productos de JELUZ
codigo_buscar = "TERM32A"
proveedor_buscar = "JELUZ"

# Consultas
consultas = [
    {
        "titulo": f"PRODUCTOS CON CÓDIGO '{codigo_buscar}'",
        "query": """
            SELECT * FROM stock 
            WHERE codigo LIKE ? OR codigo LIKE ? OR codigo LIKE ?
        """,
        "params": (f"%{codigo_buscar}%", f"%{codigo_buscar.lower()}%", f"%{codigo_buscar.upper()}%")
    },
    {
        "titulo": f"PRODUCTOS DEL PROVEEDOR '{proveedor_buscar}'",
        "query": """
            SELECT s.* 
            FROM stock s
            JOIN proveedores_manual p ON s.proveedor_id = p.id
            WHERE p.nombre LIKE ? OR p.nombre LIKE ? OR p.nombre LIKE ?
        """,
        "params": (f"%{proveedor_buscar}%", f"%{proveedor_buscar.lower()}%", f"%{proveedor_buscar.upper()}%")
    },
    {
        "titulo": "TABLAS EN LA BASE DE DATOS",
        "query": """
            SELECT name FROM sqlite_master WHERE type='table'
        """,
        "params": None
    },
    {
        "titulo": "ESTRUCTURA DE LA TABLA STOCK",
        "query": """
            PRAGMA table_info(stock)
        """,
        "params": None
    },
    {
        "titulo": "ESTRUCTURA DE LA TABLA PROVEEDORES_MANUAL",
        "query": """
            PRAGMA table_info(proveedores_manual)
        """,
        "params": None
    },
    {
        "titulo": "PRIMEROS 5 REGISTROS DE LA TABLA STOCK",
        "query": """
            SELECT * FROM stock LIMIT 5
        """,
        "params": None
    },
    {
        "titulo": "PRIMEROS 5 REGISTROS DE LA TABLA PROVEEDORES_MANUAL",
        "query": """
            SELECT * FROM proveedores_manual LIMIT 5
        """,
        "params": None
    }
]

# Ejecutar consultas en cada base de datos
for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"Base de datos '{db_path}' no encontrada")
        continue
    
    print(f"\n\n========== CONSULTANDO BASE DE DATOS: {db_path} ==========")
    
    try:
        conn = conectar_bd(db_path)
        
        for consulta in consultas:
            try:
                resultados = ejecutar_consulta(conn, consulta["query"], consulta["params"])
                mostrar_resultados(resultados, consulta["titulo"])
            except Exception as e:
                print(f"Error al ejecutar consulta '{consulta['titulo']}': {e}")
        
        conn.close()
    except Exception as e:
        print(f"Error al conectar a la base de datos '{db_path}': {e}")