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
    """Limpia la base de datos PostgreSQL en Railway."""
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
                "carrito",           # Productos en carrito
                "notificaciones"     # Notificaciones relacionadas con productos
            ]
            
            records_deleted = {}
            
            for table in tables_to_clean:
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
                    "deleted": count_before - count_after
                }
                
                print(f"Tabla '{table}' limpiada: {count_before} registros eliminados.")
            
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