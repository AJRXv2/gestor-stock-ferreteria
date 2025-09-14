import sqlite3
import pandas as pd
import os

# Función para simular la función db_query de gestor.py
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

# Función para simular parse_price de gestor.py
def parse_price(price_str):
    """Parsear precio en distintos formatos"""
    try:
        if not price_str:
            return 0.0, None
        
        if isinstance(price_str, (int, float)):
            return float(price_str), None
        
        price_str = str(price_str).replace('$', '').replace(',', '.').strip()
        if not price_str:
            return 0.0, None
        
        return float(price_str), None
    except Exception as e:
        return 0.0, str(e)

# Función mejorada para buscar productos por proveedor
def buscar_en_excel_manual_por_proveedor(termino_busqueda, proveedor_id, dueno_filtro=None):
    """Versión mejorada para buscar productos en el Excel por proveedor específico"""
    resultados = []
    EXCEL_FOLDER = "listas_excel"
    MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, "productos_manual.xlsx")
    
    try:
        print(f"[TEST] Iniciando búsqueda: término='{termino_busqueda}', proveedor_id={proveedor_id}, dueño={dueno_filtro}")
        
        if not os.path.exists(MANUAL_PRODUCTS_FILE):
            print(f"[ERROR] No se encontró el archivo de productos manuales")
            return resultados
        
        # Leer el Excel
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        print(f"[INFO] Total de productos en Excel: {len(df)}")
        print(f"[INFO] Proveedores disponibles: {df['Proveedor'].unique().tolist()}")
        
        # Obtener el nombre del proveedor
        proveedor_info = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
        if not proveedor_info:
            print(f"[ERROR] No se encontró el proveedor con ID {proveedor_id}")
            return resultados
        
        proveedor_nombre = proveedor_info[0]['nombre']
        print(f"[INFO] Proveedor: {proveedor_nombre} (ID: {proveedor_id})")
        
        # Búsqueda flexible por proveedor
        filtered_df = df[df['Proveedor'].astype(str).str.lower().str.contains(proveedor_nombre.lower(), na=False)]
        print(f"[INFO] Después de filtrar por proveedor: {len(filtered_df)} resultados")
        
        # Si no hay resultados, ignorar filtro de proveedor
        if len(filtered_df) == 0:
            print(f"[INFO] No se encontraron productos para el proveedor - ignorando filtro")
            df_for_search = df
        else:
            df_for_search = filtered_df
        
        # Filtrar por dueño si existe
        if dueno_filtro:
            df_for_search = df_for_search[df_for_search['Dueno'].astype(str).str.lower() == str(dueno_filtro).lower()]
            print(f"[INFO] Después de filtrar por dueño: {len(df_for_search)} resultados")
        
        # Filtrar por término de búsqueda
        if termino_busqueda:
            mask = (
                df_for_search['Nombre'].astype(str).str.contains(termino_busqueda, case=False, na=False) |
                df_for_search['Codigo'].astype(str).str.contains(termino_busqueda, case=False, na=False)
            )
            df_for_search = df_for_search[mask]
            print(f"[INFO] Después de filtrar por término '{termino_busqueda}': {len(df_for_search)} resultados")
        
        # Convertir a lista de resultados
        for _, row in df_for_search.iterrows():
            precio_val, _ = parse_price(row.get('Precio', ''))
            resultado = {
                'codigo': row.get('Codigo', ''),
                'nombre': row.get('Nombre', ''),
                'precio': precio_val,
                'proveedor': row.get('Proveedor', ''),
                'observaciones': row.get('Observaciones', ''),
                'dueno': row.get('Dueno', '')
            }
            resultados.append(resultado)
        
        print(f"[INFO] Resultados finales: {len(resultados)}")
        
    except Exception as e:
        print(f"[ERROR] Error en la búsqueda: {e}")
    
    return resultados

# Función para realizar pruebas
def run_tests():
    print("\n===== PRUEBA 1: BUSCAR TERM32A CON PROVEEDOR JELUZ =====")
    # Obtener el ID del proveedor JELUZ
    proveedor_info = db_query("SELECT id FROM proveedores_manual WHERE nombre = 'JELUZ'", fetch=True)
    if not proveedor_info:
        print("[ERROR] No se encontró el proveedor JELUZ en la base de datos")
        return
    
    jeluz_id = proveedor_info[0]['id']
    print(f"ID del proveedor JELUZ: {jeluz_id}")
    
    # Buscar TERM32A con proveedor JELUZ
    resultados = buscar_en_excel_manual_por_proveedor("TERM32A", jeluz_id, "ferreteria_general")
    
    print("\nResultados:")
    for i, r in enumerate(resultados, 1):
        print(f"{i}. Código: {r['codigo']}, Nombre: {r['nombre']}, Proveedor: {r['proveedor']}")
    
    print("\n===== PRUEBA 2: BUSCAR TODOS LOS PRODUCTOS DE JELUZ =====")
    resultados = buscar_en_excel_manual_por_proveedor("", jeluz_id, "ferreteria_general")
    
    print("\nResultados:")
    for i, r in enumerate(resultados, 1):
        print(f"{i}. Código: {r['codigo']}, Nombre: {r['nombre']}, Proveedor: {r['proveedor']}")
    
    print("\n===== PRUEBA 3: BUSCAR TERM32A SIN ESPECIFICAR PROVEEDOR =====")
    # Obtener el ID de un proveedor que no sea JELUZ
    otro_proveedor = db_query("SELECT id FROM proveedores_manual WHERE nombre <> 'JELUZ' LIMIT 1", fetch=True)
    if otro_proveedor:
        otro_id = otro_proveedor[0]['id']
        print(f"ID de otro proveedor para prueba: {otro_id}")
        
        resultados = buscar_en_excel_manual_por_proveedor("TERM32A", otro_id, "ferreteria_general")
        
        print("\nResultados:")
        for i, r in enumerate(resultados, 1):
            print(f"{i}. Código: {r['codigo']}, Nombre: {r['nombre']}, Proveedor: {r['proveedor']}")

# Ejecutar las pruebas
if __name__ == "__main__":
    run_tests()