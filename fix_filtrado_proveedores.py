import os
import pandas as pd
import sqlite3
from openpyxl import load_workbook
import sys

# Agregar el directorio actual al path para poder importar módulos de gestor.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Intentar importar funciones necesarias de gestor.py
try:
    from gestor import buscar_en_excel, PROVEEDOR_CONFIG
    gestor_importado = True
    print("✅ Módulos de gestor.py importados correctamente")
except ImportError as e:
    gestor_importado = False
    print(f"❌ Error al importar módulos de gestor.py: {e}")

# Configuración
MANUAL_PRODUCTS_FILE = os.path.join('listas_excel', 'productos_manual.xlsx')
DB_FILE = 'gestor_stock.db'

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def diagnosticar_problema_filtrado():
    """Diagnosticar por qué no funciona el filtrado por proveedor en la versión online"""
    print("\n=== DIAGNÓSTICO DE PROBLEMA DE FILTRADO POR PROVEEDOR ===")
    
    # Casos de prueba
    casos_prueba = [
        {"producto": "TERM32A", "proveedor": "jeluz", "dueno": "ferreteria_general"},
        {"producto": "TERM32A", "proveedor": "JELUZ", "dueno": "ferreteria_general"},
        {"producto": "TERM32A", "proveedor": None, "dueno": "ferreteria_general"},
        {"producto": "TERM60S", "proveedor": "sica", "dueno": "ferreteria_general"},
        {"producto": "TERM60S", "proveedor": "SICA", "dueno": "ferreteria_general"},
        {"producto": "TERM60S", "proveedor": None, "dueno": "ferreteria_general"}
    ]
    
    # Ejecutar cada caso de prueba
    for caso in casos_prueba:
        print(f"\n--- Caso de prueba: Producto={caso['producto']}, Proveedor={caso['proveedor']}, Dueño={caso['dueno']} ---")
        
        if not gestor_importado:
            print("❌ No se pudo importar la función buscar_en_excel de gestor.py")
            continue
        
        # Ejecutar búsqueda
        try:
            resultados = buscar_en_excel(
                termino_busqueda=caso['producto'],
                proveedor_filtro=caso['proveedor'],
                solo_fg=(caso['dueno'] == 'ferreteria_general')
            )
            
            print(f"Resultados encontrados: {len(resultados)}")
            
            if resultados:
                for i, r in enumerate(resultados, 1):
                    print(f"  {i}. Código: {r.get('codigo')}, Nombre: {r.get('nombre')}, Proveedor: {r.get('proveedor')}")
            else:
                print("  No se encontraron resultados")
                
        except Exception as e:
            print(f"❌ Error al ejecutar la búsqueda: {e}")
            import traceback
            print(traceback.format_exc())

def verificar_estructura_excel():
    """Verificar la estructura del Excel y los productos guardados"""
    print("\n=== VERIFICANDO ESTRUCTURA DEL EXCEL ===")
    
    if not os.path.exists(MANUAL_PRODUCTS_FILE):
        print(f"❌ Archivo Excel no encontrado: {MANUAL_PRODUCTS_FILE}")
        return
    
    try:
        # Leer Excel
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        print(f"Total de productos en Excel: {len(df)}")
        print("\nColumnas disponibles:")
        for col in df.columns:
            print(f"  - {col}")
        
        # Verificar productos específicos
        for codigo in ["TERM32A", "TERM60S"]:
            productos = df[df['Codigo'].astype(str).str.upper() == codigo.upper()]
            if len(productos) > 0:
                print(f"\nProducto {codigo} encontrado ({len(productos)} coincidencias):")
                for idx, row in productos.iterrows():
                    print(f"  Fila {idx}: Código={row.get('Codigo')}, Proveedor={row.get('Proveedor')}, Dueño={row.get('Dueno')}")
            else:
                print(f"\nProducto {codigo} NO encontrado")
        
        # Verificar proveedores
        proveedores = df['Proveedor'].unique()
        print("\nProveedores en Excel:")
        for i, prov in enumerate(proveedores, 1):
            productos_prov = len(df[df['Proveedor'] == prov])
            print(f"  {i}. {prov} ({productos_prov} productos)")
        
        # Verificar contenido completo
        print("\nContenido completo del Excel:")
        for idx, row in df.iterrows():
            print(f"\nFila {idx}:")
            for col in df.columns:
                print(f"  {col}: {row[col]}")
    
    except Exception as e:
        print(f"❌ Error al verificar Excel: {e}")
        import traceback
        print(traceback.format_exc())

def verificar_proveedor_config():
    """Verificar la configuración de proveedores en PROVEEDOR_CONFIG"""
    if not gestor_importado:
        print("❌ No se pudo importar PROVEEDOR_CONFIG de gestor.py")
        return
    
    print("\n=== VERIFICANDO PROVEEDOR_CONFIG ===")
    
    # Verificar JELUZ y SICA en PROVEEDOR_CONFIG
    for prov_key in ["jeluz", "sica"]:
        if prov_key in PROVEEDOR_CONFIG:
            print(f"✅ '{prov_key}' encontrado en PROVEEDOR_CONFIG")
            config = PROVEEDOR_CONFIG[prov_key]
            print(f"  Configuración:")
            for key, value in config.items():
                if not isinstance(value, list):
                    print(f"    {key}: {value}")
                else:
                    print(f"    {key}: {value[:3]}...")
        else:
            print(f"❌ '{prov_key}' NO encontrado en PROVEEDOR_CONFIG")
    
    # Verificar que las claves estén en minúsculas
    for key in PROVEEDOR_CONFIG.keys():
        if key != key.lower():
            print(f"⚠️ Advertencia: La clave '{key}' no está en minúsculas")

def analizar_configuracion():
    """Analizar la configuración de la aplicación"""
    print("\n=== ANALIZANDO CONFIGURACIÓN DE LA APLICACIÓN ===")
    
    # Verificar la configuración de la base de datos
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar proveedores_manual
            cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre IN ('SICA', 'JELUZ') ORDER BY nombre")
            proveedores = cursor.fetchall()
            
            print("\nProveedores relevantes en la base de datos:")
            for p in proveedores:
                print(f"  ID: {p['id']}, Nombre: {p['nombre']}, Dueño: {p['dueno']}")
            
            # Verificar proveedores_meta
            cursor.execute("SELECT nombre, dueno FROM proveedores_meta WHERE nombre IN ('sica', 'SICA', 'jeluz', 'JELUZ')")
            meta = cursor.fetchall()
            
            print("\nRegistros en proveedores_meta:")
            if meta:
                for m in meta:
                    print(f"  Nombre: {m['nombre']}, Dueño: {m['dueno']}")
            else:
                print("  No se encontraron registros relevantes")
            
            conn.close()
        except Exception as e:
            print(f"❌ Error al consultar base de datos: {e}")
            conn.close()

def verificar_flujo_busqueda():
    """Analizar el flujo de la búsqueda en la aplicación"""
    print("\n=== ANALIZANDO FLUJO DE BÚSQUEDA ===")
    
    print("""
    Flujo de búsqueda en buscar_en_excel:
    
    1. Si proveedor_filtro comienza con 'manual_':
       → Llama a buscar_en_excel_manual_por_proveedor
       
    2. Si proveedor_filtro está en PROVEEDOR_CONFIG:
       → Llama a buscar_en_excel_manual_por_nombre_proveedor para cada dueño
       → Busca en archivos Excel del proveedor específico
       
    3. Si no hay proveedor_filtro o no está en PROVEEDOR_CONFIG:
       → Incluye todos los productos manuales sin filtrar por proveedor
       → Busca en todos los archivos Excel disponibles
    
    Posibles problemas:
    
    1. Las claves en PROVEEDOR_CONFIG no coinciden con los valores de proveedor_filtro
       → Las claves deben estar en minúsculas, pero los filtros podrían venir en mayúsculas
       
    2. El proveedor existe en PROVEEDOR_CONFIG pero con una clave distinta
       → Ej: 'sica' vs 'SICA', o alguna variación
       
    3. El filtro de proveedor no se está pasando correctamente desde la interfaz
       → Verificar cómo se construye el parámetro proveedor_filtro en búsqueda.html
    """)
    
    # Verificar normalización de proveedores en buscar_en_excel
    if gestor_importado:
        print("\nProbemos cómo se normaliza el nombre del proveedor en buscar_en_excel:")
        try:
            import inspect
            source = inspect.getsource(buscar_en_excel)
            
            if "proveedor_filtro = proveedor_filtro.lower()" in source:
                print("✅ Se normaliza proveedor_filtro a minúsculas")
            else:
                print("❌ No se normaliza proveedor_filtro a minúsculas")
            
            print("\nProbemos si hay comparación case-insensitive entre proveedor_filtro y PROVEEDOR_CONFIG:")
            if "proveedor_filtro.lower() in [k.lower() for k in PROVEEDOR_CONFIG]" in source or similar_check(source):
                print("✅ Hay comparación case-insensitive con PROVEEDOR_CONFIG")
            else:
                print("❌ No hay comparación case-insensitive con PROVEEDOR_CONFIG")
        except Exception as e:
            print(f"❌ Error al analizar función: {e}")

def similar_check(source):
    """Verificar si hay una comparación similar case-insensitive"""
    patterns = [
        "proveedor_filtro.lower()",
        "PROVEEDOR_CONFIG.keys()",
        "str.lower()",
        "in [",
        "in {"
    ]
    return all(pattern in source for pattern in patterns)

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DE FILTRADO POR PROVEEDOR ===")
    
    # 1. Verificar estructura del Excel
    verificar_estructura_excel()
    
    # 2. Verificar PROVEEDOR_CONFIG
    verificar_proveedor_config()
    
    # 3. Analizar configuración
    analizar_configuracion()
    
    # 4. Verificar flujo de búsqueda
    verificar_flujo_busqueda()
    
    # 5. Ejecutar diagnóstico
    diagnosticar_problema_filtrado()
    
    print("\n=== DIAGNÓSTICO COMPLETO ===")