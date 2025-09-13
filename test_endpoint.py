@app.route('/obtener_proveedores_por_dueno_test', methods=['POST'])
def obtener_proveedores_por_dueno_test():
    """Endpoint de prueba sin requerir login o CSRF para probar la API"""
    try:
        data = request.get_json()
        dueno = data.get('dueno', '').strip()
        
        if not dueno:
            return jsonify({'success': False, 'msg': 'Dueño no especificado'})
        
        print(f"[DEBUG] obtener_proveedores_por_dueno_test llamado con dueño: '{dueno}'")
        
        # Usar la nueva tabla proveedores_duenos para obtener proveedores
        proveedores = db_query(
            """
            SELECT DISTINCT p.nombre 
            FROM proveedores_manual p
            JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
            WHERE pd.dueno = ?
            ORDER BY p.nombre
            """, 
            (dueno,), fetch=True
        )
        
        resultado = [p['nombre'] for p in proveedores]
        print(f"[DEBUG] obtener_proveedores_por_dueno_test - proveedores encontrados: {resultado}")
        
        return jsonify({
            'success': True,
            'proveedores': resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})