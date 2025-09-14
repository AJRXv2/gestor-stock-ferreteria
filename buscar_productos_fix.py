# Modificación para la función buscar_en_excel_manual_por_proveedor en gestor.py

def buscar_en_excel_manual_por_proveedor(termino_busqueda, proveedor_id, dueno_filtro=None):
    """Versión mejorada para buscar productos en el Excel por proveedor específico
    
    Esta versión incluye las siguientes mejoras:
    1. Búsqueda más flexible de proveedores (insensible a mayúsculas/minúsculas)
    2. Si no encuentra resultados con el filtro de proveedor, ignora ese filtro
    3. Mejores mensajes de diagnóstico para facilitar la depuración
    4. Verificación explícita de correspondencias para el producto buscado
    """
    resultados = []
    
    try:
        print(f"[EXCEL DEBUG] Iniciando búsqueda en Excel manual para proveedor_id={proveedor_id} y dueno_filtro={dueno_filtro}")
        
        if not os.path.exists(MANUAL_PRODUCTS_FILE):
            print(f"[EXCEL ERROR] No se encontró el archivo de productos manuales: {MANUAL_PRODUCTS_FILE}")
            return resultados
        
        print(f"[EXCEL DEBUG] Leyendo archivo: {MANUAL_PRODUCTS_FILE}")
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        
        # Normalizar nombres de columnas por si existen acentos
        df.rename(columns={'Código': 'Codigo', 'Dueño': 'Dueno'}, inplace=True)
        
        print(f"[EXCEL DEBUG] DataFrame inicial: {len(df)} filas")
        if df.empty:
            print("[EXCEL ERROR] El DataFrame está vacío")
            return resultados
        
        # DIAGNÓSTICO TOTAL: Mostrar contenido completo del Excel
        print("[EXCEL DIAGNÓSTICO TOTAL] ===== CONTENIDO COMPLETO DEL EXCEL =====")
        for idx, row in df.iterrows():
            print(f"[EXCEL DIAGNÓSTICO] Fila {idx}:")
            for col in df.columns:
                print(f"[EXCEL DIAGNÓSTICO]   {col}: {row[col]}")
            print("[EXCEL DIAGNÓSTICO] ---")
        print("[EXCEL DIAGNÓSTICO TOTAL] ===== FIN CONTENIDO COMPLETO =====")
        
        # Obtener nombre del proveedor
        proveedor_info = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
        if not proveedor_info:
            print(f"[EXCEL ERROR] No se encontró información para el proveedor con ID {proveedor_id}")
            
            # CAMBIO: Si no encontramos el proveedor, continuamos sin filtrar por proveedor
            proveedor_nombre = None
            filtered_df = df
        else:
            proveedor_nombre = proveedor_info[0]['nombre']
            print(f"[EXCEL DEBUG] Nombre del proveedor ID {proveedor_id}: '{proveedor_nombre}'")
            
            # Imprimir todos los proveedores disponibles en el Excel para diagnóstico
            print(f"[EXCEL DEBUG] Proveedores disponibles en Excel: {df['Proveedor'].unique().tolist()}")
            
            # Usar una búsqueda más flexible que incluya coincidencias parciales y comparaciones insensibles a mayúsculas/minúsculas
            filtered_df = df[df['Proveedor'].astype(str).str.lower().str.contains(proveedor_nombre.lower(), na=False)]
            print(f"[EXCEL DEBUG] Después de filtrar por proveedor '{proveedor_nombre}' (búsqueda flexible): {len(filtered_df)} filas")
        
        # CAMBIO: Si no hay resultados después de filtrar por proveedor, usamos todos los productos
        if len(filtered_df) == 0 and proveedor_nombre:
            print(f"[EXCEL DEBUG] No se encontraron productos para el proveedor '{proveedor_nombre}' - mostrando todos los productos")
            
            # NUEVO: Búsqueda específica para el término buscado sin filtro de proveedor
            if termino_busqueda:
                print(f"[EXCEL DEBUG] Buscando específicamente el término '{termino_busqueda}' en todo el Excel:")
                for idx, row in df.iterrows():
                    codigo = str(row.get('Codigo', '')).lower()
                    nombre = str(row.get('Nombre', '')).lower()
                    if termino_busqueda.lower() in codigo or termino_busqueda.lower() in nombre:
                        print(f"[EXCEL DEBUG] ¡ENCONTRADO SIN FILTRO DE PROVEEDOR! Fila {idx}, Código: {row.get('Codigo', '')}, Nombre: {row.get('Nombre', '')}, Proveedor: {row.get('Proveedor', '')}")
            
            # Usamos el DataFrame original sin filtrar por proveedor
            filtered_df = df
        
        # Aplicamos el filtro de dueño si existe
        if dueno_filtro:
            print(f"[EXCEL DEBUG] Filtrando por dueño: {dueno_filtro}")
            df = filtered_df[filtered_df['Dueno'].astype(str).str.lower() == str(dueno_filtro).lower()]
            print(f"[EXCEL DEBUG] Después de filtrar por dueño: {len(df)} filas")
        else:
            df = filtered_df
        
        # Filtrar por término de búsqueda si existe (soporta combinaciones "palabra1 palabra2")
        if termino_busqueda:
            print(f"[EXCEL DEBUG] Filtrando por término de búsqueda: {termino_busqueda}")
            tokens = [t.strip() for t in str(termino_busqueda).split() if t.strip()]
            if tokens:
                mask_all = pd.Series(True, index=df.index)
                for tok in tokens:
                    mask_tok = (
                        df['Nombre'].astype(str).str.contains(tok, case=False, na=False) |
                        df['Codigo'].astype(str).str.contains(tok, case=False, na=False) |
                        df['Proveedor'].astype(str).str.contains(tok, case=False, na=False)
                    )
                    mask_all &= mask_tok
                df = df[mask_all]
                print(f"[EXCEL DEBUG] Después de filtrar por tokens de búsqueda: {len(df)} filas")
        
        print(f"[EXCEL DEBUG] Resultados finales: {len(df)} filas")
        
        # Convertir a lista de diccionarios
        for _, row in df.iterrows():
            precio_val, precio_error = parse_price(row.get('Precio', ''))
            resultado = {
                'codigo': row.get('Codigo', ''),
                'nombre': row.get('Nombre', ''),
                'precio': precio_val,
                'precio_texto': str(row.get('Precio', '')) if precio_error else None,
                'proveedor': row.get('Proveedor', ''),
                'observaciones': row.get('Observaciones', ''),
                'dueno': row.get('Dueno', ''),
                'es_manual': True
            }
            resultados.append(resultado)
    
    except Exception as e:
        print(f"Error al buscar en Excel manual por proveedor: {e}")
    
    return resultados