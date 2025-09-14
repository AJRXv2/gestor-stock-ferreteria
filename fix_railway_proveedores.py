"""Script para reparar las relaciones entre proveedores y dueños en Railway (PostgreSQL)"""

def fix_provider_duenos_relations(is_postgres):
    """Repara la tabla proveedores_duenos creando las relaciones faltantes entre proveedores y dueños.
    
    Args:
        is_postgres (bool): True si estamos usando PostgreSQL, False para SQLite
        
    Returns:
        dict: Resultados de la operación con estadísticas
    """
    if is_postgres:
        import psycopg2
        import psycopg2.extras
        import os
        
        # Obtener la URL de la base de datos de PostgreSQL
        DATABASE_URL = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
        
        try:
            # Conectarse a la base de datos PostgreSQL
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Verificar la situación actual
            cursor.execute("SELECT COUNT(*) FROM proveedores_manual")
            total_providers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT proveedor_id) FROM proveedores_duenos")
            providers_with_relations_before = cursor.fetchone()[0]
            
            # Obtener todos los proveedores que no tienen relaciones en proveedores_duenos
            cursor.execute("""
                SELECT pm.id, pm.nombre, pm.dueno 
                FROM proveedores_manual pm
                LEFT JOIN proveedores_duenos pd ON pm.id = pd.proveedor_id
                WHERE pd.id IS NULL AND pm.dueno IS NOT NULL
            """)
            
            providers_to_fix = cursor.fetchall()
            affected_relationships = 0
            
            # Para cada proveedor sin relación, crear la entrada en proveedores_duenos
            for provider in providers_to_fix:
                provider_id = provider['id']
                dueno_name = provider['dueno']
                
                # Si el dueño está vacío, continuamos con el siguiente
                if not dueno_name or dueno_name.strip() == '':
                    continue
                
                # Crear la relación en proveedores_duenos
                cursor.execute("""
                    INSERT INTO proveedores_duenos (proveedor_id, dueno)
                    VALUES (%s, %s)
                    ON CONFLICT (proveedor_id, dueno) DO NOTHING
                """, (provider_id, dueno_name))
                
                affected_relationships += 1
            
            # Confirmar los cambios
            conn.commit()
            
            # Verificar el resultado
            cursor.execute("SELECT COUNT(DISTINCT proveedor_id) FROM proveedores_duenos")
            providers_with_relations_after = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM proveedores_duenos")
            total_relations = cursor.fetchone()[0]
            
            # Cerrar la conexión
            cursor.close()
            conn.close()
            
            # Devolver estadísticas
            return {
                'providers_analyzed': total_providers,
                'providers_with_relations_before': providers_with_relations_before,
                'providers_with_relations_after': providers_with_relations_after,
                'affected_relationships': affected_relationships,
                'total_relations_created': total_relations - (total_relations - affected_relationships)
            }
            
        except Exception as e:
            # Si ocurre un error, lo registramos y devolvemos información del error
            import traceback
            error_traceback = traceback.format_exc()
            
            return {
                'error': str(e),
                'traceback': error_traceback,
                'success': False
            }
    else:
        # Para SQLite, simplemente devolver un mensaje informativo
        return {
            'message': 'Esta función solo es aplicable a PostgreSQL en Railway',
            'success': False
        }