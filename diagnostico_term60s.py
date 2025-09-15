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

def verificar_term60s_en_excel():
    """Verificar si TERM60S está en el Excel de productos manuales"""
    print("\n=== VERIFICANDO PRODUCTO TERM60S EN EXCEL ===")
    
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
        print("\nBúsqueda por código 'TERM60S':")
        busqueda_exacta = df[df['Codigo'].astype(str).str.upper() == 'TERM60S']
        if len(busqueda_exacta) > 0:
            print(f"¡ENCONTRADO! {len(busqueda_exacta)} coincidencias exactas:")
            for idx, row in busqueda_exacta.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron coincidencias exactas para 'TERM60S'")
        
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
        
        # Filtrar por proveedor SICA
        print("\nProductos del proveedor 'SICA':")
        proveedores_sica = df[df['Proveedor'].astype(str).str.upper() == 'SICA']
        if len(proveedores_sica) > 0:
            print(f"¡ENCONTRADO! {len(proveedores_sica)} productos de SICA:")
            for idx, row in proveedores_sica.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron productos de proveedor 'SICA'")
        
        # Buscar coincidencias parciales de proveedor
        print("\nProductos con proveedor que contiene 'SICA':")
        proveedores_sica_parcial = df[df['Proveedor'].astype(str).str.upper().str.contains('SICA')]
        if len(proveedores_sica_parcial) > 0:
            print(f"¡ENCONTRADO! {len(proveedores_sica_parcial)} productos con proveedor que contiene 'SICA':")
            for idx, row in proveedores_sica_parcial.iterrows():
                print(f"Fila {idx}:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("No se encontraron productos con proveedor que contiene 'SICA'")
        
        # Listar todos los proveedores
        print("\nLista de todos los proveedores en el Excel:")
        proveedores = df['Proveedor'].unique()
        for i, prov in enumerate(proveedores, 1):
            print(f"{i}. {prov}")
    
    except Exception as e:
        print(f"Error al buscar en Excel: {e}")
        import traceback
        print(traceback.format_exc())

def verificar_sica_en_proveedor_config():
    """Verificar si SICA está correctamente configurado en el PROVEEDOR_CONFIG"""
    print("\n=== VERIFICANDO SICA EN PROVEEDOR_CONFIG ===")
    
    # Verificar archivo gestor.py manualmente
    gestor_path = 'gestor.py'
    sica_encontrado = False
    
    try:
        with open(gestor_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        en_proveedor_config = False
        config_completo = False
        
        for i, linea in enumerate(lineas):
            if 'PROVEEDOR_CONFIG = {' in linea:
                en_proveedor_config = True
            
            if en_proveedor_config and "'sica': {" in linea.lower():
                sica_encontrado = True
                print(f"¡ENCONTRADO! 'sica' está en PROVEEDOR_CONFIG en línea {i+1}")
                
                # Mostrar la configuración completa
                config = []
                j = i
                nivel_llaves = 0
                
                while j < len(lineas):
                    config.append(lineas[j].strip())
                    nivel_llaves += lineas[j].count('{') - lineas[j].count('}')
                    
                    if nivel_llaves == 0 and '},' in lineas[j]:
                        config_completo = True
                        break
                    j += 1
                
                if config_completo:
                    print("Configuración completa:")
                    for c in config:
                        print(f"  {c}")
                else:
                    print("No se pudo encontrar la configuración completa")
                
                break
        
        if not sica_encontrado:
            print("'sica' NO se encontró en PROVEEDOR_CONFIG")
    
    except Exception as e:
        print(f"Error al verificar PROVEEDOR_CONFIG: {e}")

def verificar_duenos_config():
    """Verificar DUENOS_CONFIG para asegurar que SICA esté correctamente configurado"""
    print("\n=== VERIFICANDO DUENOS_CONFIG ===")
    
    gestor_path = 'gestor.py'
    sica_encontrado = False
    
    try:
        with open(gestor_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        en_duenos_config = False
        
        for i, linea in enumerate(lineas):
            if 'DUENOS_CONFIG = {' in linea:
                en_duenos_config = True
            
            if en_duenos_config and "'proveedores_excel': [" in linea:
                # Buscar si SICA está en la lista de proveedores
                j = i
                while j < len(lineas) and ']' not in lineas[j]:
                    if "'sica'" in lineas[j].lower():
                        print(f"¡ENCONTRADO! 'sica' está en la lista de proveedores_excel en línea {j+1}:")
                        print(f"  {lineas[j].strip()}")
                        sica_encontrado = True
                        break
                    j += 1
            
            if en_duenos_config and '}' in linea and linea.strip() == '}':
                # Fin de DUENOS_CONFIG
                en_duenos_config = False
                break
        
        if not sica_encontrado:
            print("'sica' NO se encontró en la lista de proveedores_excel")
    
    except Exception as e:
        print(f"Error al verificar DUENOS_CONFIG: {e}")

def verificar_archivos_excel():
    """Verificar si existen archivos Excel de SICA"""
    print("\n=== VERIFICANDO ARCHIVOS EXCEL DE SICA ===")
    
    # Buscar en carpetas de Excel
    carpetas_excel = ['listas_excel', 'listas_excel/ferreteria_general', 'listas_excel/ricky']
    
    for carpeta in carpetas_excel:
        if os.path.exists(carpeta):
            print(f"\nArchivos en carpeta: {carpeta}")
            archivos = [f for f in os.listdir(carpeta) if f.lower().startswith('sica') and f.endswith('.xlsx')]
            if archivos:
                print(f"¡ENCONTRADOS! {len(archivos)} archivos de SICA:")
                for i, archivo in enumerate(archivos, 1):
                    print(f"{i}. {archivo}")
            else:
                print("No se encontraron archivos Excel de SICA")
        else:
            print(f"La carpeta {carpeta} no existe")

if __name__ == "__main__":
    print("Diagnóstico para TERM60S y SICA")
    print("==============================")
    
    # Verificar producto en Excel
    verificar_term60s_en_excel()
    
    # Verificar configuración de SICA
    verificar_sica_en_proveedor_config()
    verificar_duenos_config()
    
    # Verificar archivos Excel
    verificar_archivos_excel()
    
    print("\nDiagnóstico completado.")