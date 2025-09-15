# Funciones auxiliares para diagnosticar y corregir problemas con proveedores en Railway (PostgreSQL)

def diagnosticar_proveedores():
    """Diagnostica el estado de los proveedores y sus relaciones en la base de datos.
    
    Verifica si hay proveedores sin dueños asociados, lo cual causa que no aparezcan
    en las secciones de agregar productos y gestionar productos.
    
    Returns:
        dict: Un diccionario con los resultados del diagnóstico
    """
    resultados = {
        'proveedores_total': 0,
        'proveedores_sin_dueno': [],
        'duenos': []
    }
    
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}
    
    try:
        # Verificar proveedores sin dueños asociados
        query_proveedores_sin_dueno = """
        SELECT p.id, p.nombre
        FROM proveedores_manual p
        LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        WHERE pd.proveedor_id IS NULL
        ORDER BY p.nombre
        """
        
        sin_dueno = db_query(query_proveedores_sin_dueno, fetch=True, conn=conn)
        
        # Obtener todos los proveedores para estadísticas
        query_todos_proveedores = "SELECT COUNT(*) as total FROM proveedores_manual"
        total = db_query(query_todos_proveedores, fetch=True, conn=conn)
        
        # Obtener dueños existentes
        query_duenos = "SELECT DISTINCT dueno FROM proveedores_duenos"
        duenos = db_query(query_duenos, fetch=True, conn=conn)
        
        resultados['proveedores_total'] = total[0]['total'] if total else 0
        resultados['proveedores_sin_dueno'] = sin_dueno if sin_dueno else []
        resultados['duenos'] = [d['dueno'] for d in duenos] if duenos else []
        
        # Verificar tabla proveedores_duenos
        if _is_postgres_configured():
            # Verificar índices en PostgreSQL
            indices_query = """
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'proveedores_duenos'
            """
            indices = db_query(indices_query, fetch=True, conn=conn)
            resultados['indices'] = [idx['indexname'] for idx in indices] if indices else []
        
    except Exception as e:
        resultados['error'] = f"Error durante el diagnóstico: {str(e)}"
    finally:
        try:
            conn.close()
        except:
            pass
    
    return resultados

def corregir_proveedores_sin_dueno():
    """Corrige el problema de proveedores sin dueños asociados.
    
    Asocia automáticamente los proveedores sin dueño a ambos dueños
    ('ricky' y 'ferreteria_general') para garantizar su visibilidad.
    
    Returns:
        dict: Un diccionario con los resultados de la corrección
    """
    resultados = {
        'corregidos': 0,
        'errores': [],
        'proveedores': []
    }
    
    # Primero diagnosticar
    diagnostico = diagnosticar_proveedores()
    if 'error' in diagnostico:
        return {"error": diagnostico['error']}
    
    if not diagnostico['proveedores_sin_dueno']:
        return {"mensaje": "No hay proveedores sin dueño que corregir", "corregidos": 0}
    
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}
    
    try:
        for p in diagnostico['proveedores_sin_dueno']:
            proveedor_id = p['id']
            nombre = p['nombre']
            
            # Asociar a ambos dueños
            duenos = ['ricky', 'ferreteria_general']
            proveedor_corregido = True
            
            for d in duenos:
                # Insertar en proveedores_duenos
                ok_duenos = db_query(
                    "INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)",
                    (proveedor_id, d),
                    conn=conn
                )
                
                # Insertar en proveedores_meta (legacy)
                ok_meta = db_query(
                    "INSERT OR IGNORE INTO proveedores_meta (nombre, dueno) VALUES (?, ?)",
                    (nombre, d),
                    conn=conn
                )
                
                if not (ok_duenos and ok_meta):
                    proveedor_corregido = False
                    resultados['errores'].append(f"Error al asociar proveedor '{nombre}' a dueño '{d}'")
            
            if proveedor_corregido:
                resultados['corregidos'] += 1
                resultados['proveedores'].append(nombre)
    
    except Exception as e:
        resultados['error'] = f"Error durante la corrección: {str(e)}"
    finally:
        try:
            conn.close()
        except:
            pass
    
    return resultados

def verificar_indices_pg():
    """Verifica y crea índices necesarios en PostgreSQL para mejorar el rendimiento.
    
    Esta función solo hace algo en entorno PostgreSQL (Railway).
    
    Returns:
        dict: Un diccionario con los resultados de la verificación
    """
    if not _is_postgres_configured():
        return {"mensaje": "No es necesario verificar índices en SQLite"}
    
    resultados = {
        'indices_creados': 0,
        'errores': []
    }
    
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}
    
    try:
        # Índices para proveedores_duenos
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno)"
        ]
        
        for idx_query in indices:
            ok = db_query(idx_query, conn=conn)
            if ok:
                resultados['indices_creados'] += 1
            else:
                resultados['errores'].append(f"Error al crear índice: {idx_query}")
    
    except Exception as e:
        resultados['error'] = f"Error durante la verificación de índices: {str(e)}"
    finally:
        try:
            conn.close()
        except:
            pass
    
    return resultados