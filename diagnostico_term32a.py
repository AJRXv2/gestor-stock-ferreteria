import os
import pandas as pd
import sqlite3
from openpyxl import load_workbook

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

def check_term32a_in_excel():
    """Verificar si TERM32A está en el Excel de productos manuales"""
    print("\n=== VERIFICANDO PRODUCTO EN EXCEL ===")
    
    if not os.path.exists(MANUAL_PRODUCTS_FILE):
        print(f"Archivo de productos manuales no encontrado: {MANUAL_PRODUCTS_FILE}")
        return
    
    try:
        # Cargar Excel
        print(f"Leyendo archivo: {MANUAL_PRODUCTS_FILE}")
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        print(f"Total de productos en Excel: {len(df)}")
        
        # Normalizar nombres de columnas
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        # Buscar por código
        print("\nBúsqueda por código 'TERM32A':")
        busqueda_exacta = df[df['Codigo'].astype(str).str.upper() == 'TERM32A']
        if len(busqueda_exacta) > 0:
            print(f"¡ENCONTRADO! {len(busqueda_exacta)} coincidencias exactas:")
            for idx, row in busqueda_exacta.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron coincidencias exactas para 'TERM32A'")
        
        # Buscar coincidencias parciales
        print("\nBúsqueda por coincidencia parcial 'TERM':")
        busqueda_parcial = df[df['Codigo'].astype(str).str.upper().str.contains('TERM')]
        if len(busqueda_parcial) > 0:
            print(f"¡ENCONTRADO! {len(busqueda_parcial)} coincidencias parciales:")
            for idx, row in busqueda_parcial.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron coincidencias parciales para 'TERM'")
        
        # Filtrar por proveedor JELUZ
        print("\nProductos del proveedor 'JELUZ':")
        proveedores_jeluz = df[df['Proveedor'].astype(str).str.upper() == 'JELUZ']
        if len(proveedores_jeluz) > 0:
            print(f"¡ENCONTRADO! {len(proveedores_jeluz)} productos de JELUZ:")
            for idx, row in proveedores_jeluz.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron productos de proveedor 'JELUZ'")
        
        # Buscar coincidencias parciales de proveedor
        print("\nProductos con proveedor que contiene 'JEL':")
        proveedores_jel = df[df['Proveedor'].astype(str).str.upper().str.contains('JEL')]
        if len(proveedores_jel) > 0:
            print(f"¡ENCONTRADO! {len(proveedores_jel)} productos con proveedor que contiene 'JEL':")
            for idx, row in proveedores_jel.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron productos con proveedor que contiene 'JEL'")
            
        # Listar todos los proveedores
        print("\nLista de todos los proveedores en el Excel:")
        proveedores = df['Proveedor'].unique()
        for i, prov in enumerate(proveedores, 1):
            print(f"{i}. {prov}")
    
    except Exception as e:
        print(f"Error al buscar en Excel: {e}")
        import traceback
        print(traceback.format_exc())

def check_term32a_in_database():
    """Verificar si TERM32A está en la base de datos"""
    print("\n=== VERIFICANDO PRODUCTO EN BASE DE DATOS ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Buscar en tabla de stock
        cursor = conn.cursor()
        
        # Buscar en stock
        print("\nBúsqueda en tabla 'stock':")
        cursor.execute("SELECT * FROM stock WHERE codigo LIKE ? OR codigo LIKE ?", ('TERM32A', '%TERM32A%'))
        results = cursor.fetchall()
        if results:
            print(f"¡ENCONTRADO! {len(results)} coincidencias en 'stock':")
            for row in results:
                print_row_dict(dict(row))
        else:
            print("No se encontraron coincidencias en 'stock'")
        
        # Buscar en productos_manual
        print("\nBúsqueda en tabla 'productos_manual':")
        cursor.execute("SELECT * FROM productos_manual WHERE codigo LIKE ? OR codigo LIKE ?", ('TERM32A', '%TERM32A%'))
        results = cursor.fetchall()
        if results:
            print(f"¡ENCONTRADO! {len(results)} coincidencias en 'productos_manual':")
            for row in results:
                print_row_dict(dict(row))
        else:
            print("No se encontraron coincidencias en 'productos_manual'")
        
        # Buscar productos de JELUZ
        print("\nProductos del proveedor 'JELUZ' en 'stock':")
        cursor.execute("SELECT * FROM stock WHERE proveedor LIKE ?", ('%JELUZ%',))
        results = cursor.fetchall()
        if results:
            print(f"¡ENCONTRADO! {len(results)} productos de JELUZ en 'stock':")
            for row in results:
                print_row_dict(dict(row))
        else:
            print("No se encontraron productos de JELUZ en 'stock'")
        
        # Buscar en productos_manual
        print("\nProductos del proveedor 'JELUZ' en 'productos_manual':")
        cursor.execute("""
            SELECT pm.*, p.nombre as proveedor_nombre 
            FROM productos_manual pm
            JOIN proveedores_manual p ON pm.proveedor_id = p.id
            WHERE p.nombre LIKE ?
        """, ('%JELUZ%',))
        results = cursor.fetchall()
        if results:
            print(f"¡ENCONTRADO! {len(results)} productos de JELUZ en 'productos_manual':")
            for row in results:
                print_row_dict(dict(row))
        else:
            print("No se encontraron productos de JELUZ en 'productos_manual'")
        
        # Listar todos los proveedores
        print("\nLista de todos los proveedores en la base de datos:")
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual ORDER BY nombre")
        results = cursor.fetchall()
        for i, row in enumerate(results, 1):
            print(f"{i}. ID: {row['id']}, Nombre: {row['nombre']}, Dueño: {row['dueno']}")
    
    except Exception as e:
        print(f"Error al buscar en base de datos: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        conn.close()

def print_row_dict(row_dict):
    """Imprime un diccionario de forma legible"""
    print("{")
    for key, value in row_dict.items():
        print(f"  {key}: {value}")
    print("}")

if __name__ == "__main__":
    print("Diagnóstico para TERM32A")
    print("========================")
    
    check_term32a_in_excel()
    check_term32a_in_database()
    
    print("\nDiagnóstico completado.")