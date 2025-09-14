import pandas as pd
import os

# Obtener la ruta al archivo Excel
excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listas_excel', 'productos_manual.xlsx')

print(f"Verificando archivo: {excel_path}")
print(f"¿Existe el archivo? {os.path.exists(excel_path)}")

try:
    # Leer el archivo Excel
    df = pd.read_excel(excel_path)
    
    print(f"\n===== INFORMACIÓN DEL EXCEL =====")
    print(f"Número total de productos: {len(df)}")
    print(f"Columnas disponibles: {df.columns.tolist()}")
    
    # Mostrar un resumen de los proveedores
    print(f"\n===== PROVEEDORES EN EL EXCEL =====")
    proveedores = df['Proveedor'].unique()
    print(f"Número de proveedores únicos: {len(proveedores)}")
    for i, prov in enumerate(proveedores, 1):
        count = len(df[df['Proveedor'] == prov])
        print(f"{i}. '{prov}' - {count} productos")
    
    # Buscar el producto específico TERM32A
    print(f"\n===== BÚSQUEDA DE PRODUCTO TERM32A =====")
    term32a_df = df[df['Codigo'].astype(str).str.contains('TERM32A', case=False)]
    
    if len(term32a_df) > 0:
        print(f"¡PRODUCTO ENCONTRADO! - {len(term32a_df)} coincidencia(s)")
        for _, row in term32a_df.iterrows():
            print(f"Código: {row.get('Codigo', '')}")
            print(f"Nombre: {row.get('Nombre', '')}")
            print(f"Proveedor: {row.get('Proveedor', '')}")
            print(f"Precio: {row.get('Precio', '')}")
            print(f"Observaciones: {row.get('Observaciones', '')}")
            print(f"Dueño: {row.get('Dueno', '')}")
    else:
        print(f"Producto TERM32A no encontrado en el Excel")
    
    # Buscar productos de JELUZ
    print(f"\n===== BÚSQUEDA DE PRODUCTOS DE JELUZ =====")
    jeluz_df = df[df['Proveedor'].astype(str).str.contains('JELUZ', case=False)]
    
    if len(jeluz_df) > 0:
        print(f"Productos de JELUZ encontrados: {len(jeluz_df)}")
        for i, (_, row) in enumerate(jeluz_df.iterrows(), 1):
            print(f"{i}. Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}")
    else:
        print(f"No se encontraron productos del proveedor JELUZ")
    
    # Mostrar las primeras 5 filas del Excel para referencia
    print(f"\n===== PRIMERAS 5 FILAS DEL EXCEL =====")
    for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
        print(f"Fila {i}:")
        for col in df.columns:
            print(f"  {col}: {row[col]}")
        print("---")
    
except Exception as e:
    print(f"Error al leer el Excel: {e}")