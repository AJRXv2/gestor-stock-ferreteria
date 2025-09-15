"""
Script para actualizar las funciones de eliminación de productos manuales
para utilizar la base de datos en lugar del archivo Excel.
"""

import re

def get_replacement_code():
    """Devuelve el código de reemplazo para las funciones de eliminación"""
    
    return """
@app.route('/manual_eliminar_seleccionados_ajax', methods=['POST'])
@login_required
def manual_eliminar_seleccionados_ajax():
    """Eliminar productos seleccionados de la tabla productos_manual."""
    try:
        data = request.get_json(silent=True) or {}
        codigos = data.get('codigos', [])
        if not codigos:
            return jsonify({'success': False, 'msg': 'No se especificaron códigos.'})
        
        # Eliminar de la base de datos
        placeholders = ', '.join(['?'] * len(codigos))
        res = db_query(f"DELETE FROM productos_manual WHERE codigo IN ({placeholders})", tuple(codigos))
        
        eliminados = res.rowcount if hasattr(res, 'rowcount') else 0
        print(f"[DB INFO] Eliminados {eliminados} productos manualmente seleccionados.")
        
        # Actualizar el Excel para mantener compatibilidad
        try:
            export_db_to_excel()
        except Exception as e_excel:
            print(f"[DB WARN] No se pudo actualizar el Excel: {e_excel}")
        
        return jsonify({'success': True, 'msg': f'Eliminados {eliminados} código(s).', 'eliminados': eliminados})
    except Exception as e:
        return jsonify({'success': False, 'msg': f'Error: {str(e)}'})

@app.route('/manual_eliminar_por_proveedor_ajax', methods=['POST'])
@login_required
def manual_eliminar_por_proveedor_ajax():
    """Eliminar TODOS los productos manuales de un proveedor específico (por proveedor_id + dueño).
    Request JSON: { proveedor_id: int, dueno: 'ricky'|'ferreteria_general' }
    - Borra de la tabla productos_manual donde proveedor coincide y opcionalmente dueño.
    - Actualiza el Excel para mantener compatibilidad.
    """
    try:
        data = request.get_json(silent=True) or {}
        proveedor_id = data.get('proveedor_id')
        dueno = (data.get('dueno') or '').strip().lower() or None
        if not proveedor_id:
            return jsonify({'success': False, 'msg': 'Falta proveedor_id.'})

        # Obtener nombre del proveedor desde proveedores_manual
        prov_rows = db_query("SELECT nombre, dueno FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
        if not prov_rows:
            return jsonify({'success': False, 'msg': 'Proveedor no encontrado.'})
        proveedor_nombre = prov_rows[0]['nombre']
        dueno_prov = (prov_rows[0].get('dueno') or '').lower() if isinstance(prov_rows[0], dict) else dueno

        # Criterios de eliminación en BD
        condiciones_sql = ["proveedor = ?"]
        params = [proveedor_nombre]
        if dueno and dueno_prov and dueno_prov == dueno:
            condiciones_sql.append("(dueno IS NULL OR LOWER(dueno)=?)")
            params.append(dueno)
        
        # Eliminar productos
        result = db_query(f"DELETE FROM productos_manual WHERE {' AND '.join(condiciones_sql)}", tuple(params))
        deleted_count = result.rowcount if hasattr(result, 'rowcount') else 0
        
        # Actualizar el Excel para mantener compatibilidad
        try:
            export_db_to_excel()
        except Exception as e_excel:
            print(f"[DB WARN] No se pudo actualizar el Excel: {e_excel}")
        
        return jsonify({
            'success': True,
            'msg': f'Eliminados {deleted_count} productos del proveedor {proveedor_nombre}.',
            'eliminados': deleted_count
        })
    except Exception as e:
        print(f"[DB ERROR] Error eliminando productos por proveedor: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'msg': f'Error: {str(e)}'})
"""

def get_replace_patterns():
    """Devuelve los patrones para buscar las funciones a reemplazar"""
    return {
        'manual_eliminar_seleccionados_ajax': re.compile(
            r'@app\.route\(\'/manual_eliminar_seleccionados_ajax\', methods=\[\'POST\'\]\)[^#]*?return jsonify\({\'success\': False, \'msg\': f\'Error: {[^}]*}\'\}\)', 
            re.DOTALL
        ),
        'manual_eliminar_por_proveedor_ajax': re.compile(
            r'@app\.route\(\'/manual_eliminar_por_proveedor_ajax\', methods=\[\'POST\'\]\)[^#]*?return jsonify\({\'success\': False, \'msg\': f\'Error: {[^}]*}\'\}\)', 
            re.DOTALL
        )
    }

def update_gestor_file():
    """Actualiza el archivo gestor.py con las nuevas funciones"""
    
    gestor_file = 'gestor.py'
    
    try:
        # Leer el contenido actual del archivo
        with open(gestor_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Obtener patrones y código de reemplazo
        patterns = get_replace_patterns()
        replacement = get_replacement_code()
        
        # Dividir el reemplazo en las dos funciones
        parts = replacement.split('@app.route')
        
        # La primera parte contiene sólo un salto de línea, ignorar
        manual_eliminar_seleccionados = '@app.route' + parts[1]
        manual_eliminar_por_proveedor = '@app.route' + parts[2]
        
        # Reemplazar cada función
        if patterns['manual_eliminar_seleccionados_ajax'].search(content):
            content = patterns['manual_eliminar_seleccionados_ajax'].sub(manual_eliminar_seleccionados, content)
            print("Función manual_eliminar_seleccionados_ajax actualizada")
        else:
            print("No se encontró la función manual_eliminar_seleccionados_ajax")
            return False
        
        if patterns['manual_eliminar_por_proveedor_ajax'].search(content):
            content = patterns['manual_eliminar_por_proveedor_ajax'].sub(manual_eliminar_por_proveedor, content)
            print("Función manual_eliminar_por_proveedor_ajax actualizada")
        else:
            print("No se encontró la función manual_eliminar_por_proveedor_ajax")
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
    print("Actualizando funciones de eliminación de productos manuales...")
    if update_gestor_file():
        print("✅ Actualización completada exitosamente")
    else:
        print("❌ Error en la actualización")