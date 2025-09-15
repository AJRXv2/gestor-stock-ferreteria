#!/usr/bin/env python3
"""
Script para corregir la función buscar_en_excel_manual_por_nombre_proveedor
"""

import re

def fix_manual_search_function():
    """Reemplaza la función problemática con la versión correcta"""
    
    # Leer el archivo actual
    with open('gestor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Función correcta que busca en la base de datos
    correct_function = '''def buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, nombre_proveedor, dueno_filtro=None):
    """Buscar en la tabla productos_manual por nombre de proveedor. Permite filtrar por dueño."""
    resultados = []
    try:
        print(f"[DB DEBUG] Buscando por nombre de proveedor en DB. Término: '{termino_busqueda}', Proveedor: '{nombre_proveedor}', Dueño: {dueno_filtro}")
        
        # Construir consulta SQL
        query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(?)"
        params = [nombre_proveedor]
        
        if dueno_filtro:
            query += " AND LOWER(dueno) = LOWER(?)"
            params.append(dueno_filtro)
            
        if termino_busqueda:
            tokens = [t.strip() for t in str(termino_busqueda).split() if t.strip()]
            if tokens:
                or_conditions = []
                for token in tokens:
                    or_conditions.append("(LOWER(nombre) LIKE LOWER(?) OR LOWER(codigo) LIKE LOWER(?))")
                    params.extend([f"%{token}%", f"%{token}%"])
                query += f" AND ({' AND '.join(or_conditions)})"
        
        # Ejecutar consulta
        rows = db_query(query, tuple(params), fetch=True)
        print(f"[DB DEBUG] Resultados: {len(rows) if rows else 0} productos")
        
        # Convertir resultados al formato esperado
        for row in (rows or []):
            precio_val, precio_error = parse_price(str(row.get('precio', '')))
            resultados.append({
                'codigo': row.get('codigo', ''),
                'nombre': row.get('nombre', ''),
                'precio': precio_val,
                'precio_texto': str(row.get('precio', '')) if precio_error else None,
                'proveedor': row.get('proveedor', ''),
                'observaciones': row.get('observaciones', ''),
                'dueno': row.get('dueno', ''),
                'es_manual': True
            })
            
    except Exception as e:
        print(f"[DB ERROR] Error en buscar_en_excel_manual_por_nombre_proveedor: {e}")
        import traceback
        print(traceback.format_exc())
    return resultados'''
    
    # Buscar y reemplazar la función problemática
    # Patrón para encontrar la función completa (desde def hasta return resultados)
    pattern = r'def buscar_en_excel_manual_por_nombre_proveedor\([^)]*\):.*?return resultados'
    
    # Reemplazar con la función correcta
    new_content = re.sub(pattern, correct_function, content, flags=re.DOTALL)
    
    # Escribir el archivo corregido
    with open('gestor.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Función corregida exitosamente")

if __name__ == "__main__":
    fix_manual_search_function()
