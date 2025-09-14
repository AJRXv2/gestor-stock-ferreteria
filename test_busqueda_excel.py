import pandas as pd
import sqlite3
import os

# Rutas y constantes
EXCEL_FOLDER = "listas_excel"
MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, "productos_manual.xlsx")

# Función para ejecutar consultas en la base de datos
def db_query(query, params=None, fetch=False):
    try:
        conn = sqlite3.connect("gestor_stock.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = True
        
        conn.close()
        return result
    except Exception as e:
        print(f"Error en consulta a la base de datos: {e}")
        return [] if fetch else False

# Función para parsear precios (simulada)
def parse_price(price_str):
    try:
        if not price_str:
            return 0.0, None
        
        # Convertir a float si es posible
        if isinstance(price_str, (int, float)):
            return float(price_str), None
        
        # Limpiar la cadena
        clean_price = str(price_str).replace('$', '').replace(',', '.').strip()
        return float(clean_price), None
    except Exception as e:
        return 0.0, str(e)

# Función simplificada para buscar en el Excel
def buscar_en_excel_manual(termino_busqueda=None):
    """Busca todos los productos en el Excel de productos manuales"""
    resultados = []
    
    try:
        if not os.path.exists(MANUAL_PRODUCTS_FILE):
            print(f"No se encontró el archivo: {MANUAL_PRODUCTS_FILE}")
            return resultados
        
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        # Normalizar nombres de columnas
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        print(f"Total de productos en Excel: {len(df)}")
        
        # Filtrar por término de búsqueda si existe
        if termino_busqueda:
            mask = (
                df['Nombre'].astype(str).str.contains(termino_busqueda, case=False, na=False) |
                df['Codigo'].astype(str).str.contains(termino_busqueda, case=False, na=False) |
                df['Proveedor'].astype(str).str.contains(termino_busqueda, case=False, na=False)
            )
            df = df[mask]
            print(f"Después de filtrar por '{termino_busqueda}': {len(df)} coincidencias")
        
        # Convertir a lista de diccionarios
        for _, row in df.iterrows():
            resultado = {
                'codigo': row.get('Codigo', ''),
                'nombre': row.get('Nombre', ''),
                'precio': row.get('Precio', 0.0),
                'proveedor': row.get('Proveedor', ''),
                'observaciones': row.get('Observaciones', ''),
                'dueno': row.get('Dueno', '')
            }
            resultados.append(resultado)
        
    except Exception as e:
        print(f"Error al buscar en Excel: {e}")
    
    return resultados

# Función para buscar por proveedor
def buscar_en_excel_por_proveedor(proveedor_id, termino_busqueda=None):
    """Busca productos en el Excel filtrando por proveedor"""
    resultados = []
    
    try:
        if not os.path.exists(MANUAL_PRODUCTS_FILE):
            print(f"No se encontró el archivo: {MANUAL_PRODUCTS_FILE}")
            return resultados
        
        # Obtener el nombre del proveedor
        proveedor_info = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
        if not proveedor_info:
            print(f"No se encontró proveedor con ID {proveedor_id}")
            return resultados
        
        proveedor_nombre = proveedor_info[0]['nombre']
        print(f"Buscando productos del proveedor: {proveedor_nombre} (ID: {proveedor_id})")
        
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        # Normalizar nombres de columnas
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        print(f"Total de productos en Excel: {len(df)}")
        print(f"Proveedores disponibles: {df['Proveedor'].unique().tolist()}")
        
        # Filtrar por proveedor (búsqueda flexible)
        filtered_df = df[df['Proveedor'].astype(str).str.lower().str.contains(proveedor_nombre.lower(), na=False)]
        print(f"Después de filtrar por proveedor '{proveedor_nombre}': {len(filtered_df)} coincidencias")
        
        # Si no hay resultados, mostrar todos los productos
        if len(filtered_df) == 0:
            print(f"No se encontraron productos para el proveedor '{proveedor_nombre}' - mostrando todos")
            filtered_df = df
        
        # Filtrar por término de búsqueda si existe
        if termino_busqueda:
            mask = (
                filtered_df['Nombre'].astype(str).str.contains(termino_busqueda, case=False, na=False) |
                filtered_df['Codigo'].astype(str).str.contains(termino_busqueda, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
            print(f"Después de filtrar por '{termino_busqueda}': {len(filtered_df)} coincidencias")
        
        # Convertir a lista de diccionarios
        for _, row in filtered_df.iterrows():
            resultado = {
                'codigo': row.get('Codigo', ''),
                'nombre': row.get('Nombre', ''),
                'precio': row.get('Precio', 0.0),
                'proveedor': row.get('Proveedor', ''),
                'observaciones': row.get('Observaciones', ''),
                'dueno': row.get('Dueno', '')
            }
            resultados.append(resultado)
        
    except Exception as e:
        print(f"Error al buscar en Excel por proveedor: {e}")
    
    return resultados

# Realizar las pruebas de búsqueda
print("\n========== PRUEBA 1: BUSCAR TODOS LOS PRODUCTOS ==========")
productos = buscar_en_excel_manual()
print(f"Se encontraron {len(productos)} productos en total:")
for i, p in enumerate(productos, 1):
    print(f"{i}. {p['codigo']} - {p['nombre']} (Proveedor: {p['proveedor']})")

print("\n========== PRUEBA 2: BUSCAR TERM32A ==========")
productos = buscar_en_excel_manual("TERM32A")
print(f"Se encontraron {len(productos)} productos con 'TERM32A':")
for i, p in enumerate(productos, 1):
    print(f"{i}. {p['codigo']} - {p['nombre']} (Proveedor: {p['proveedor']})")

print("\n========== PRUEBA 3: BUSCAR POR PROVEEDOR JELUZ ==========")
# Primero obtenemos el ID del proveedor JELUZ
proveedor_jeluz = db_query("SELECT id FROM proveedores_manual WHERE nombre = 'JELUZ'", fetch=True)
if proveedor_jeluz:
    jeluz_id = proveedor_jeluz[0]['id']
    print(f"ID del proveedor JELUZ: {jeluz_id}")
    
    productos = buscar_en_excel_por_proveedor(jeluz_id)
    print(f"Se encontraron {len(productos)} productos del proveedor JELUZ:")
    for i, p in enumerate(productos, 1):
        print(f"{i}. {p['codigo']} - {p['nombre']} (Proveedor: {p['proveedor']})")
else:
    print("No se encontró el proveedor JELUZ en la base de datos")