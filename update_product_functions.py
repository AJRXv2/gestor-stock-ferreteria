"""
Script para actualizar las funciones de gestión (agregar/editar/eliminar) de productos manuales
para utilizar la base de datos en lugar del archivo Excel.
"""

import re

def get_replacement_code():
    """Devuelve el código de reemplazo para la función agregar_producto_manual_excel"""
    
    return """
def agregar_producto_manual_excel():
    """Agregar producto manual a la base de datos (no directamente al stock)"""
    try:
        codigo = request.form.get('codigo', '').strip()
        proveedor_id = request.form.get('proveedor_id', '').strip()
        nombre = request.form.get('nombre', '').strip()
        precio_str = request.form.get('precio', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        dueno = request.form.get('dueno_nuevo_proveedor', '').strip()
        
        # Validaciones
        if not nombre:
            flash('El nombre del producto es obligatorio.', 'danger')
            return redirect(url_for('agregar_producto'))
        
        if not dueno:
            flash('Debe seleccionar un dueño para el producto.', 'danger')
            return redirect(url_for('agregar_producto'))
        
        # Obtener nombre del proveedor si se proporcionó proveedor_id
        proveedor_nombre = ''
        if proveedor_id:
            proveedor_data = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
            if proveedor_data:
                proveedor_nombre = proveedor_data[0]['nombre']
        
        # Procesar precio
        precio = 0.0
        if precio_str:
            precio, error_precio = parse_price(precio_str)
            if error_precio:
                flash(f'Error en el precio: {precio_str}', 'warning')
                precio = 0.0
        
        # Insertar en la base de datos
        result = db_query(
            "INSERT INTO productos_manual (codigo, proveedor, nombre, precio, observaciones, dueno) VALUES (?, ?, ?, ?, ?, ?)",
            (codigo, proveedor_nombre, nombre, precio, observaciones, dueno)
        )
        
        if result:
            dueno_nombre = DUENOS_CONFIG.get(dueno, {}).get('nombre', dueno)
            flash(f'Producto "{nombre}" agregado a la lista manual de {dueno_nombre}. Puede buscarlo en "Buscar en Excel".', 'success')
            
            # Actualizar el Excel para mantener compatibilidad
            try:
                export_db_to_excel()
            except Exception as e_excel:
                print(f"[DB WARN] No se pudo actualizar el Excel: {e_excel}")
        else:
            flash('Error al agregar el producto a la lista manual.', 'danger')
            
    except Exception as e:
        flash(f'Error al procesar el producto: {str(e)}', 'danger')
        
    return redirect(url_for('agregar_producto'))
"""

def get_replace_pattern():
    """Devuelve el patrón para buscar la función a reemplazar"""
    return re.compile(r'def agregar_producto_manual_excel\(\):[^#]*?return redirect\(url_for\(\'agregar_producto\'\)\)', re.DOTALL)

def update_gestor_file():
    """Actualiza el archivo gestor.py con la nueva función"""
    
    gestor_file = 'gestor.py'
    
    try:
        # Leer el contenido actual del archivo
        with open(gestor_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Obtener patrón y código de reemplazo
        pattern = get_replace_pattern()
        replacement = get_replacement_code()
        
        # Reemplazar la función
        if pattern.search(content):
            content = pattern.sub(replacement, content)
            print(f"Función agregar_producto_manual_excel actualizada")
        else:
            print("No se encontró la función agregar_producto_manual_excel")
            return False
        
        # Guardar los cambios
        with open(gestor_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Archivo {gestor_file} actualizado exitosamente")
        return True
    except Exception as e:
        print(f"Error actualizando {gestor_file}: {e}")
        return False

if __name__ == "__main__":
    print("Actualizando funciones de gestión de productos manuales...")
    if update_gestor_file():
        print("✅ Actualización completada exitosamente")
    else:
        print("❌ Error en la actualización")