#!/usr/bin/env python3
"""
Script para corregir la función buscar_en_excel_manual
"""

def fix_buscar_manual():
    """Reemplaza la función buscar_en_excel_manual para que busque en la base de datos"""
    
    # Leer el archivo actual
    with open('gestor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Nueva función que busca en la base de datos
    new_function = '''def buscar_en_excel_manual(termino_busqueda, dueno_filtro=None):
    """Buscar en la tabla productos_manual de la base de datos sin proveedor específico. Permite filtrar por dueño."""
    resultados = []
    try:
        print(f"[DB DEBUG] Iniciando búsqueda en DB manual. Término: '{termino_busqueda}', Dueño: {dueno_filtro}")
        
        # Construir consulta SQL
        query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE 1=1"
        params = []
        
        if dueno_filtro:
            query += " AND LOWER(dueno) = LOWER(?)"
            params.append(dueno_filtro)
            
        if termino_busqueda:
            tokens = [t.strip() for t in str(termino_busqueda).split() if t.strip()]
            if tokens:
                or_conditions = []
                for token in tokens:
                    or_conditions.append("(LOWER(nombre) LIKE LOWER(?) OR LOWER(codigo) LIKE LOWER(?) OR LOWER(proveedor) LIKE LOWER(?))")
                    params.extend([f"%{token}%", f"%{token}%", f"%{token}%"])
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
        print(f"[DB ERROR] Error en buscar_en_excel_manual: {e}")
        import traceback
        print(traceback.format_exc())
    return resultados'''
    
    # Buscar y reemplazar la función
    import re
    pattern = r'def buscar_en_excel_manual\(termino_busqueda, dueno_filtro=None\):.*?return resultados'
    
    # Reemplazar con la nueva función
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Escribir el archivo corregido
    with open('gestor.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Función buscar_en_excel_manual corregida para buscar en base de datos")

if __name__ == "__main__":
    fix_buscar_manual()
