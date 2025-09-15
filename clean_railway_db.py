"""
Script para limpiar la base de datos PostgreSQL en Railway.
Elimina todos los registros de productos pero mantiene la estructura de las tablas
y la configuración de proveedores.
"""

import os
import json
import psycopg2
from datetime import datetime

def clean_railway_db():
    """Limpia la base de datos PostgreSQL en Railway.
    
    Esta función ejecuta la limpieza mejorada en el script limpiar_tablas_railway.py,
    que incluye la eliminación directa de productos problemáticos específicos.
    """
    try:
        # Importar la función mejorada de limpieza
        from limpiar_tablas_railway import limpiar_tablas_railway
        
        # Ejecutar la limpieza mejorada
        resultado = limpiar_tablas_railway()
        
        # Si la importación y ejecución funciona, devolver el resultado
        return resultado
    except ImportError:
        # Si no se puede importar el módulo mejorado, usar la implementación original
        print("No se pudo importar limpiar_tablas_railway.py, usando implementación original")
        return _clean_railway_db_original()

def _clean_railway_db_original():
    """Implementación original de la limpieza de la base de datos.
    Se usa como fallback si no se puede importar el módulo mejorado.
    """
    # Verificar si estamos en Railway (PostgreSQL)
    if not os.environ.get('DATABASE_URL') and not os.path.exists('railway.json'):
        print("Este script debe ejecutarse en Railway con PostgreSQL configurado.")
        return {
            "success": False,
            "mensaje": "Este script debe ejecutarse en Railway con PostgreSQL configurado."
        }
    
    try:
        # Conectar a la base de datos PostgreSQL
        dsn = os.environ.get('DATABASE_URL')
        
        # Si estamos en local y hay un archivo railway.json, usar eso
        if not dsn and os.path.exists('railway.json'):
            with open('railway.json', 'r') as f:
                railway_config = json.load(f)
                dsn = railway_config.get('POSTGRES_URL', '')
        
        if not dsn:
            return {
                "success": False,
                "mensaje": "No se encontró DATABASE_URL en las variables de entorno ni en railway.json"
            }
        
        # Convertir postgres:// a postgresql:// si es necesario
        if dsn.startswith('postgres://'):
            dsn = dsn.replace('postgres://', 'postgresql://')
        
        conn = psycopg2.connect(dsn)
        conn.autocommit = False  # Usar transacciones para poder hacer rollback
        cur = conn.cursor()
        
        # Registrar el momento de inicio de la limpieza
        timestamp = datetime.now().isoformat()
        
        try:
            # 1. Eliminar registros de tablas relacionadas con productos
            tables_to_clean = [
                "productos_manual",  # Productos manuales
                "stock",             # Productos en stock
                "stock_history",     # Historial de stock
                "carrito"            # Productos en carrito
                # Omitimos "notificaciones" porque la tabla no existe
            ]
            
            # Imprimir contenido actual de stock para diagnóstico
            try:
                print("Verificando contenido actual de la tabla stock:")
                cur.execute("SELECT id, codigo, producto, proveedor FROM stock LIMIT 10")
                stock_items = cur.fetchall()
                for item in stock_items:
                    print(f"Item en stock: {item}")
            except Exception as e:
                print(f"Error al consultar tabla stock: {e}")
                
            # Forzar eliminación directa de los productos problemáticos
            problem_products = [
                {"codigo": "PROD002", "nombre": "PRODUCTO01"},
                {"codigo": "TERM50A", "nombre": "TERMICA 50a"},
                {"codigo": "TERM32A", "nombre": "TERMICA 32A"}
            ]
            
            for product in problem_products:
                try:
                    # Eliminar por código
                    cur.execute("DELETE FROM stock WHERE LOWER(codigo) = LOWER(%s)", (product["codigo"],))
                    # Eliminar por nombre
                    cur.execute("DELETE FROM stock WHERE LOWER(producto) = LOWER(%s)", (product["nombre"],))
                    print(f"Eliminación forzada de producto: {product['nombre']} ({product['codigo']})")
                except Exception as e:
                    print(f"Error en eliminación forzada: {e}")
            
            records_deleted = {}
            
            for table in tables_to_clean:
                try:
                    # Verificar si la tabla existe antes de intentar eliminar registros
                    if dsn.startswith('postgresql'):
                        # Consulta para PostgreSQL
                        cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = %s
                            );
                        """, (table,))
                    else:
                        # Consulta para SQLite
                        cur.execute(f"""
                            SELECT COUNT(name) FROM sqlite_master 
                            WHERE type='table' AND name='{table}';
                        """)
                    
                    table_exists = cur.fetchone()[0]
                    
                    if not table_exists:
                        print(f"Tabla '{table}' no existe, omitiendo.")
                        records_deleted[table] = {
                            "before": 0,
                            "after": 0,
                            "deleted": 0,
                            "exists": False
                        }
                        continue
                    
                    # Contar registros antes de eliminar para informar
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count_before = cur.fetchone()[0]
                    
                    # Eliminar los registros
                    cur.execute(f"DELETE FROM {table}")
                    
                    # Contar registros después para confirmar
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count_after = cur.fetchone()[0]
                    
                    records_deleted[table] = {
                        "before": count_before,
                        "after": count_after,
                        "deleted": count_before - count_after,
                        "exists": True
                    }
                    
                    print(f"Tabla '{table}' limpiada: {count_before} registros eliminados.")
                    
                except Exception as e:
                    print(f"Error limpiando tabla '{table}': {e}")
                    records_deleted[table] = {
                        "error": str(e),
                        "exists": False
                    }
            
            # Importante: NO eliminar estas tablas:
            # - proveedores_manual: contiene los proveedores
            # - proveedores_duenos: asociaciones entre proveedores y dueños
            # - proveedores_meta: metadata de proveedores
            # - users: usuarios del sistema
            
            # Hacer commit de los cambios
            conn.commit()
            
            return {
                "success": True,
                "mensaje": f"Base de datos limpiada exitosamente el {timestamp}",
                "tablas_limpiadas": tables_to_clean,
                "registros_eliminados": records_deleted
            }
        
        except Exception as e:
            # En caso de error, hacer rollback para evitar cambios parciales
            conn.rollback()
            return {
                "success": False,
                "error": str(e),
                "mensaje": "Error al limpiar la base de datos. No se aplicaron cambios."
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mensaje": "Error al conectar con la base de datos."
        }
    finally:
        try:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()
        except:
            pass

if __name__ == "__main__":
    resultado = clean_railway_db()
    print(resultado)