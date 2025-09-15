"""
Script para actualizar las funciones de búsqueda en productos manuales
para utilizar la base de datos en lugar del archivo Excel.
"""

import re

def get_replacement_functions():
    """Devuelve el código de las nuevas funciones para reemplazar
    las funciones existentes en gestor.py"""
    
    return """
def buscar_en_excel_manual(termino_busqueda, dueno_filtro=None):
    """Buscar en la tabla productos_manual sin proveedor específico. Permite filtrar por dueño."""
    resultados = []
    try:
        print(f"[DB DEBUG] Iniciando búsqueda en DB productos_manual. Término: '{termino_busqueda}', Dueño: {dueno_filtro}")
        
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
        
        # Si no hay resultados y se especificó un término de búsqueda, mostrar todos los productos del dueño
        if (not rows or len(rows) == 0) and termino_busqueda and dueno_filtro:
            print(f"[DB DEBUG] No se encontraron coincidencias exactas para '{termino_busqueda}', mostrando todos los productos disponibles para '{dueno_filtro}'")
            query_all = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(dueno) = LOWER(?)"
            rows = db_query(query_all, (dueno_filtro,), fetch=True)
            print(f"[DB DEBUG] Resultados sin filtro: {len(rows) if rows else 0} productos")
            
            # Convertir resultados al formato esperado
            for row in (rows or []):
                precio_val, precio_error = parse_price(str(row.get('precio', '')))
                resultados.append({
                    'codigo': row.get('codigo', ''),
                    'nombre': row.get('nombre', '') + " [SIN FILTRO]",  # Marcar que no coincide con el filtro
                    'precio': precio_val,
                    'precio_texto': str(row.get('precio', '')) if precio_error else None,
                    'proveedor': row.get('proveedor', ''),
                    'observaciones': row.get('observaciones', ''),
                    'dueno': row.get('dueno', ''),
                    'es_manual': True
                })
            return resultados
        
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
    return resultados

def buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, nombre_proveedor, dueno_filtro=None):
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
        
        # Si no hay resultados y se especificó un término de búsqueda, mostrar todos los productos del proveedor
        if (not rows or len(rows) == 0) and termino_busqueda:
            print(f"[DB DEBUG] No se encontraron coincidencias para '{termino_busqueda}', mostrando todos los productos del proveedor '{nombre_proveedor}'")
            query_all = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(?)"
            params_all = [nombre_proveedor]
            if dueno_filtro:
                query_all += " AND LOWER(dueno) = LOWER(?)"
                params_all.append(dueno_filtro)
            
            rows = db_query(query_all, tuple(params_all), fetch=True)
            print(f"[DB DEBUG] Resultados sin filtro de término: {len(rows) if rows else 0} productos")
            
            # Convertir resultados al formato esperado
            for row in (rows or []):
                precio_val, precio_error = parse_price(str(row.get('precio', '')))
                resultados.append({
                    'codigo': row.get('codigo', ''),
                    'nombre': row.get('nombre', '') + " [SIN FILTRO]",  # Marcar que no coincide con el filtro
                    'precio': precio_val,
                    'precio_texto': str(row.get('precio', '')) if precio_error else None,
                    'proveedor': row.get('proveedor', ''),
                    'observaciones': row.get('observaciones', ''),
                    'dueno': row.get('dueno', ''),
                    'es_manual': True
                })
            return resultados
        
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
    return resultados

def buscar_en_excel_manual_por_proveedor(termino_busqueda, proveedor_id, dueno_filtro=None):
    """Buscar en la tabla productos_manual por ID de proveedor. Permite filtrar por dueño."""
    try:
        print(f"[DB DEBUG] Buscando por ID de proveedor. Término: '{termino_busqueda}', Proveedor ID: {proveedor_id}, Dueño: {dueno_filtro}")
        
        # Obtener el nombre del proveedor
        prov_data = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
        if not prov_data:
            print(f"[DB ERROR] Proveedor con ID {proveedor_id} no encontrado")
            return []
        
        nombre_proveedor = prov_data[0]['nombre']
        
        # Usar la función de búsqueda por nombre de proveedor
        return buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, nombre_proveedor, dueno_filtro)
    except Exception as e:
        print(f"[DB ERROR] Error en buscar_en_excel_manual_por_proveedor: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def agregar_producto_excel_manual(codigo, proveedor, nombre, precio, observaciones, dueno):
    """Agrega un producto a la tabla productos_manual."""
    try:
        print(f"[DB DEBUG] Agregando producto manual a DB. Código: {codigo}, Proveedor: {proveedor}, Nombre: {nombre}")
        
        # Insertar en la base de datos
        result = db_query("""
            INSERT INTO productos_manual (codigo, proveedor, nombre, precio, observaciones, dueno)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (codigo, proveedor, nombre, precio, observaciones, dueno))
        
        if result:
            print(f"[DB DEBUG] Producto agregado correctamente a la base de datos")
            
            # También actualizar el Excel para mantener compatibilidad
            try:
                export_db_to_excel()
            except Exception as e_excel:
                print(f"[DB WARN] No se pudo actualizar el Excel: {e_excel}")
            
            return True
        else:
            print("[DB ERROR] Error insertando el producto en la base de datos")
            return False
    except Exception as e:
        print(f"[DB ERROR] Error en agregar_producto_excel_manual: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def export_db_to_excel():
    """Exporta los datos de la tabla productos_manual al Excel."""
    try:
        import pandas as pd
        
        # Obtener datos de la base de datos
        rows = db_query("""
            SELECT codigo as Codigo, proveedor as Proveedor, nombre as Nombre, 
                   precio as Precio, observaciones as Observaciones, dueno as Dueno 
            FROM productos_manual
        """, fetch=True)
        
        if not rows:
            print("[DB WARN] No hay productos para exportar al Excel")
            return False
        
        # Convertir a DataFrame
        df = pd.DataFrame(rows)
        
        # Renombrar columnas para mantener formato original
        if 'Codigo' in df.columns and 'Código' not in df.columns:
            df.rename(columns={'Codigo': 'Código'}, inplace=True)
        if 'Dueno' in df.columns and 'Dueño' not in df.columns:
            df.rename(columns={'Dueno': 'Dueño'}, inplace=True)
        
        # Guardar en Excel
        with pd.ExcelWriter(MANUAL_PRODUCTS_FILE, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)
        
        print(f"[DB DEBUG] Datos exportados al Excel: {MANUAL_PRODUCTS_FILE}")
        return True
    except Exception as e:
        print(f"[DB ERROR] Error exportando datos al Excel: {e}")
        import traceback
        print(traceback.format_exc())
        return False
"""

def get_function_patterns():
    """Devuelve patrones de las funciones a reemplazar en gestor.py"""
    
    return {
        # Patrón para buscar_en_excel_manual
        'buscar_en_excel_manual': re.compile(r'def buscar_en_excel_manual\([^)]*\):[^#]*?return resultados', re.DOTALL),
        
        # Patrón para buscar_en_excel_manual_por_nombre_proveedor
        'buscar_en_excel_manual_por_nombre_proveedor': re.compile(r'def buscar_en_excel_manual_por_nombre_proveedor\([^)]*\):[^#]*?return resultados', re.DOTALL),
        
        # Patrón para buscar_en_excel_manual_por_proveedor
        'buscar_en_excel_manual_por_proveedor': re.compile(r'def buscar_en_excel_manual_por_proveedor\([^)]*\):[^#]*?return [a-zA-Z_][a-zA-Z0-9_]*', re.DOTALL),
        
        # Patrón para agregar_producto_excel_manual
        'agregar_producto_excel_manual': re.compile(r'def agregar_producto_excel_manual\([^)]*\):[^#]*?return [a-zA-Z_][a-zA-Z0-9_]*', re.DOTALL)
    }

def update_gestor_file():
    """Actualiza el archivo gestor.py con las nuevas funciones"""
    
    gestor_file = 'gestor.py'
    
    try:
        # Leer el contenido actual del archivo
        with open(gestor_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Obtener patrones y nuevas funciones
        patterns = get_function_patterns()
        new_functions = get_replacement_functions()
        
        # Verificar si export_db_to_excel ya existe
        if 'def export_db_to_excel(' not in content:
            # Si no existe, agregar la función después de agregar_producto_excel_manual
            if patterns['agregar_producto_excel_manual'].search(content):
                content = patterns['agregar_producto_excel_manual'].sub(
                    lambda m: m.group(0) + '\n\n' + new_functions.split('def export_db_to_excel(')[1].split('def ')[0],
                    content
                )
        
        # Reemplazar cada función
        for func_name, pattern in patterns.items():
            if func_name != 'export_db_to_excel':  # Esta ya la tratamos por separado
                # Extraer la nueva función del texto completo
                func_pattern = re.compile(f'def {func_name}\\([^)]*\\):[^#]*?return [a-zA-Z_][a-zA-Z0-9_]*', re.DOTALL)
                new_func_match = func_pattern.search(new_functions)
                
                if new_func_match and pattern.search(content):
                    new_func = new_func_match.group(0)
                    content = pattern.sub(new_func, content)
                    print(f"Función {func_name} actualizada")
        
        # Guardar los cambios
        with open(gestor_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Archivo {gestor_file} actualizado exitosamente")
        return True
    except Exception as e:
        print(f"Error actualizando {gestor_file}: {e}")
        return False

if __name__ == "__main__":
    print("Actualizando funciones de búsqueda en productos manuales...")
    if update_gestor_file():
        print("✅ Actualización completada exitosamente")
    else:
        print("❌ Error en la actualización")