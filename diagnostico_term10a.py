import pandas as pd
import os
import sqlite3

# Funciones de utilidad
def db_query(query, params=None, fetch=False):
    """Ejecutar consulta en la base de datos"""
    conn = sqlite3.connect("gestor_stock.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = True
        
        conn.close()
        return result
    except Exception as e:
        print(f"Error en consulta a la base de datos: {e}")
        conn.close()
        return [] if fetch else False

# Rutas
EXCEL_FOLDER = "listas_excel"
MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, "productos_manual.xlsx")

print("\n===== DIAGNÓSTICO DE BÚSQUEDA POR PROVEEDOR =====")

# 1. Verificar si el archivo Excel existe
print(f"\n1. Verificando archivo Excel: {MANUAL_PRODUCTS_FILE}")
if not os.path.exists(MANUAL_PRODUCTS_FILE):
    print(f"ERROR: El archivo Excel no existe: {MANUAL_PRODUCTS_FILE}")
else:
    print(f"OK: El archivo Excel existe")

    # 2. Leer el contenido del Excel
    print("\n2. Leyendo contenido del Excel...")
    try:
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        print(f"OK: Se encontraron {len(df)} productos en el Excel")
        
        # Normalizar nombres de columnas
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        # 3. Mostrar todos los productos en el Excel
        print("\n3. Lista completa de productos en el Excel:")
        for idx, row in df.iterrows():
            print(f"   [{idx}] Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}, Dueño: {row.get('Dueno', '')}")

        # 4. Buscar específicamente TERM10A
        print("\n4. Buscando específicamente TERM10A:")
        term10a_rows = df[df['Codigo'].astype(str).str.contains('TERM10A', case=False)]
        if len(term10a_rows) > 0:
            print(f"   ¡Encontrado! {len(term10a_rows)} coincidencias:")
            for idx, row in term10a_rows.iterrows():
                print(f"   Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}, Dueño: {row.get('Dueno', '')}")
        else:
            print("   No se encontró ningún producto con código TERM10A")
            
            # Buscar productos similares
            term_rows = df[df['Codigo'].astype(str).str.contains('TERM', case=False)]
            if len(term_rows) > 0:
                print(f"   Se encontraron {len(term_rows)} productos con 'TERM' en el código:")
                for idx, row in term_rows.iterrows():
                    print(f"   Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}")
        
        # 5. Verificar proveedor JELUZ
        print("\n5. Verificando productos con proveedor JELUZ:")
        jeluz_rows = df[df['Proveedor'].astype(str).str.contains('JELUZ', case=False)]
        if len(jeluz_rows) > 0:
            print(f"   ¡Encontrado! {len(jeluz_rows)} productos con proveedor JELUZ:")
            for idx, row in jeluz_rows.iterrows():
                print(f"   Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}")
        else:
            print("   No se encontró ningún producto con proveedor JELUZ")
            
    except Exception as e:
        print(f"ERROR al leer el Excel: {e}")

# 6. Verificar la base de datos para JELUZ
print("\n6. Verificando proveedor JELUZ en la base de datos:")
proveedor_jeluz = db_query("SELECT * FROM proveedores_manual WHERE nombre LIKE '%JELUZ%'", fetch=True)
if proveedor_jeluz:
    print(f"   ¡Encontrado! {len(proveedor_jeluz)} registros:")
    for p in proveedor_jeluz:
        print(f"   ID: {p['id']}, Nombre: {p['nombre']}, Dueño: {p.get('dueno', 'N/A')}")
else:
    print("   No se encontró el proveedor JELUZ en la base de datos")

# 7. Simular la lógica de búsqueda
print("\n7. Simulando búsqueda con filtro por proveedor JELUZ:")
try:
    proveedor_id = None
    proveedor_info = db_query("SELECT id FROM proveedores_manual WHERE nombre LIKE '%JELUZ%'", fetch=True)
    if proveedor_info:
        proveedor_id = proveedor_info[0]['id']
        print(f"   ID del proveedor JELUZ: {proveedor_id}")
        
        # Simular búsqueda
        if df is not None and proveedor_id is not None:
            # Obtener nombre del proveedor
            proveedor_nombre = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)[0]['nombre']
            print(f"   Nombre del proveedor: {proveedor_nombre}")
            
            # Filtrar por proveedor
            filtered_df = df[df['Proveedor'].astype(str).str.lower().str.contains(proveedor_nombre.lower(), na=False)]
            print(f"   Después de filtrar por proveedor: {len(filtered_df)} resultados")
            
            if len(filtered_df) > 0:
                for idx, row in filtered_df.iterrows():
                    print(f"   Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}")
            
            # Buscar TERM10A específicamente
            search_term = "TERM10A"
            mask = (
                filtered_df['Nombre'].astype(str).str.contains(search_term, case=False, na=False) |
                filtered_df['Codigo'].astype(str).str.contains(search_term, case=False, na=False)
            )
            search_results = filtered_df[mask]
            print(f"   Después de filtrar por '{search_term}': {len(search_results)} resultados")
            
            if len(search_results) > 0:
                for idx, row in search_results.iterrows():
                    print(f"   Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}")
    else:
        print("   No se pudo obtener el ID del proveedor JELUZ")
except Exception as e:
    print(f"ERROR al simular la búsqueda: {e}")

print("\n===== FIN DEL DIAGNÓSTICO =====")