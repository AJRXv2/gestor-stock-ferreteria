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

def check_proveedor_config():
    """Verificar contenido de PROVEEDOR_CONFIG"""
    print("\n=== VERIFICANDO PROVEEDOR_CONFIG ===")
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        # 1. Obtener todos los proveedores manuales
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual ORDER BY nombre")
        proveedores = cursor.fetchall()
        
        print(f"Total de proveedores en la BD: {len(proveedores)}")
        print("\nProveedores manuales en BD:")
        for i, prov in enumerate(proveedores, 1):
            print(f"{i}. ID: {prov['id']}, Nombre: {prov['nombre']}, Dueño: {prov['dueno'] or 'No especificado'}")
        
        # 2. Verificar si JELUZ está en proveedores_manual
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre LIKE ?", ('%JELUZ%',))
        jeluz = cursor.fetchone()
        if jeluz:
            print(f"\nProveedor JELUZ encontrado en la BD:")
            print(f"  ID: {jeluz['id']}, Nombre: {jeluz['nombre']}, Dueño: {jeluz['dueno'] or 'No especificado'}")
        else:
            print("\nProveedor JELUZ NO encontrado en la BD")
            
        # 3. Verificar si hay registros en proveedores_meta
        cursor.execute("SELECT COUNT(*) as total FROM proveedores_meta")
        result = cursor.fetchone()
        total_meta = result['total'] if result else 0
        
        print(f"\nTotal de registros en proveedores_meta: {total_meta}")
        
        # 4. Verificar registros específicos en proveedores_meta
        cursor.execute("SELECT nombre, dueno FROM proveedores_meta WHERE nombre LIKE ? OR dueno = ?", 
                      ('%JELUZ%', 'ferreteria_general'))
        meta_records = cursor.fetchall()
        
        print("\nRegistros relevantes en proveedores_meta:")
        if meta_records:
            for i, rec in enumerate(meta_records, 1):
                print(f"{i}. Nombre: {rec['nombre']}, Dueño: {rec['dueno']}")
        else:
            print("No se encontraron registros relevantes")
            
        # 5. Verificar dueño de JELUZ en proveedores_meta
        cursor.execute("SELECT dueno FROM proveedores_meta WHERE nombre LIKE ?", ('%JELUZ%',))
        dueno_jeluz = cursor.fetchone()
        
        if dueno_jeluz:
            print(f"\nDueño de JELUZ en proveedores_meta: {dueno_jeluz['dueno']}")
        else:
            print("\nNo se encontró registro de JELUZ en proveedores_meta")
        
        # 6. Verificar productos en Excel por proveedor
        if os.path.exists(MANUAL_PRODUCTS_FILE):
            df = pd.read_excel(MANUAL_PRODUCTS_FILE)
            df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
            
            # Contar productos por proveedor
            proveedores_excel = df['Proveedor'].value_counts().to_dict()
            
            print("\nProductos por proveedor en Excel:")
            for prov, count in proveedores_excel.items():
                print(f"  {prov}: {count} productos")
                
            # Verificar productos de JELUZ
            productos_jeluz = df[df['Proveedor'].astype(str).str.upper() == 'JELUZ']
            
            print(f"\nProductos de JELUZ en Excel: {len(productos_jeluz)}")
            if len(productos_jeluz) > 0:
                for idx, row in productos_jeluz.iterrows():
                    print(f"  Fila {idx}: Código={row['Codigo']}, Nombre={row['Nombre']}, Dueño={row['Dueno']}")
        else:
            print(f"\nArchivo Excel no encontrado: {MANUAL_PRODUCTS_FILE}")
        
        # Verificar configuración en la aplicación
        print("\n=== CONCLUSIÓN ===")
        print("Para que la búsqueda funcione correctamente en buscar_en_excel (gestor.py), debe ocurrir lo siguiente:")
        print("1. JELUZ debe estar en PROVEEDOR_CONFIG para que se llame a buscar_en_excel_manual_por_nombre_proveedor")
        print("2. Si JELUZ no está en PROVEEDOR_CONFIG:")
        print("   a. Puede ser porque se considera un proveedor manual y debe buscarse usando proveedor_filtro='manual_3182_ferreteria_general'")
        print("   b. O necesita agregarse a PROVEEDOR_CONFIG para que sea reconocido correctamente")
        
        print("\nSoluciones posibles:")
        print("1. Verificar PROVEEDOR_CONFIG en gestor.py y asegurarse de que JELUZ esté incluido")
        print("2. Modificar la interfaz para que genere el filtro correcto para JELUZ (manual_3182_ferreteria_general)")
        print("3. Modificar buscar_en_excel para que busque también en productos manuales para todos los proveedores")
    
    except Exception as e:
        print(f"Error en verificación: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Verificación de configuración de proveedores")
    print("===========================================")
    
    check_proveedor_config()
    
    print("\nVerificación completada.")