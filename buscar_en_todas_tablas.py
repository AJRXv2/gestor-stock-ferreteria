import sqlite3
import os

# Función para ejecutar una consulta segura
def ejecutar_consulta_segura(conn, query, params=None):
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error en consulta: {e}")
        return []

# Función para buscar en todas las tablas
def buscar_en_todas_tablas(conn, valor_buscar):
    print(f"\n===== BUSCANDO '{valor_buscar}' EN TODAS LAS TABLAS =====")
    
    # Obtener lista de tablas
    tablas = ejecutar_consulta_segura(conn, "SELECT name FROM sqlite_master WHERE type='table'")
    if not tablas:
        print("No se encontraron tablas en la base de datos")
        return
    
    tablas = [tabla[0] for tabla in tablas]
    print(f"Tablas disponibles: {tablas}")
    
    for tabla in tablas:
        print(f"\n----- Buscando en tabla '{tabla}' -----")
        
        # Obtener columnas de la tabla
        columnas = ejecutar_consulta_segura(conn, f"PRAGMA table_info({tabla})")
        if not columnas:
            print(f"No se pudieron obtener las columnas de la tabla '{tabla}'")
            continue
        
        # Filtrar solo columnas de texto para la búsqueda
        columnas_texto = [col[1] for col in columnas if 'TEXT' in col[2].upper() or 'VARCHAR' in col[2].upper() or 'CHAR' in col[2].upper()]
        if not columnas_texto:
            print(f"No hay columnas de texto en la tabla '{tabla}' para buscar")
            continue
        
        print(f"Buscando en columnas: {columnas_texto}")
        
        # Construir consulta para buscar en cada columna de texto
        for columna in columnas_texto:
            query = f"SELECT * FROM {tabla} WHERE {columna} LIKE ?"
            resultados = ejecutar_consulta_segura(conn, query, (f"%{valor_buscar}%",))
            
            if resultados:
                print(f"¡ENCONTRADO! {len(resultados)} resultados en columna '{columna}':")
                for i, resultado in enumerate(resultados, 1):
                    print(f"Resultado {i}:")
                    for idx, col in enumerate(columnas):
                        col_name = col[1]
                        if idx < len(resultado):
                            print(f"  {col_name}: {resultado[idx]}")
            else:
                print(f"No se encontraron resultados en columna '{columna}'")

# Archivo principal de base de datos
db_path = "gestor_stock.db"

if not os.path.exists(db_path):
    print(f"Base de datos '{db_path}' no encontrada")
    exit(1)

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print(f"Conectado a base de datos: {db_path}")

# Buscar TERM32A en todas las tablas
buscar_en_todas_tablas(conn, "TERM32A")

# Buscar JELUZ en todas las tablas
buscar_en_todas_tablas(conn, "JELUZ")

# Cerrar conexión
conn.close()
print("\n===== BÚSQUEDA FINALIZADA =====")