"""
Script para actualizar la tabla proveedores_meta basándose en los datos de proveedores_duenos.
"""
import sqlite3
import sys
import os

def db_query(query, params=(), fetch=False):
    """Ejecuta una consulta en la base de datos y opcionalmente devuelve resultados."""
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        result = cursor.execute(query, params)
        if fetch:
            return [dict(row) for row in result.fetchall()]
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en consulta: {query}  \nParams: {params}\nError: {str(e)}")
        return None
    finally:
        conn.close()

def sincronizar_proveedores_meta():
    """Sincroniza proveedores_meta con los datos de proveedores_duenos."""
    print("\n=== SINCRONIZAR PROVEEDORES_META CON PROVEEDORES_DUENOS ===\n")
    
    # 1. Verificar si existe la tabla proveedores_meta
    try:
        meta_exists = db_query("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table' AND name='proveedores_meta'", fetch=True)
        if not meta_exists or meta_exists[0]['count'] == 0:
            print("La tabla proveedores_meta no existe. Creándola...")
            db_query("""
                CREATE TABLE proveedores_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    dueno TEXT NOT NULL
                )
            """)
            print("✅ Tabla proveedores_meta creada correctamente.")
        else:
            print("Tabla proveedores_meta encontrada.")
            
            # Limpiar tabla existente
            db_query("DELETE FROM proveedores_meta")
            print("Tabla proveedores_meta limpiada para actualización.")
    except Exception as e:
        print(f"Error al verificar/crear tabla proveedores_meta: {e}")
        return
    
    # 2. Obtener los datos de proveedores_duenos
    relaciones = db_query("""
        SELECT p.id, p.nombre, pd.dueno
        FROM proveedores_manual p
        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        ORDER BY p.nombre, pd.dueno
    """, fetch=True)
    
    if not relaciones:
        print("❌ No se encontraron relaciones en proveedores_duenos.")
        return
    
    print(f"Se encontraron {len(relaciones)} relaciones para sincronizar.")
    
    # 3. Insertar los datos en proveedores_meta
    for rel in relaciones:
        result = db_query(
            "INSERT INTO proveedores_meta (nombre, dueno) VALUES (?, ?)",
            (rel['nombre'], rel['dueno'])
        )
        if not result:
            print(f"❌ Error al insertar relación para {rel['nombre']} ({rel['dueno']}).")
    
    # 4. Verificar la sincronización
    meta_count = db_query("SELECT COUNT(*) as count FROM proveedores_meta", fetch=True)[0]['count']
    print(f"\nTotal de registros en proveedores_meta después de la sincronización: {meta_count}")
    
    # Listar algunos ejemplos
    ejemplos = db_query("SELECT nombre, dueno FROM proveedores_meta LIMIT 10", fetch=True)
    print("\nEjemplos de registros en proveedores_meta:")
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"   {i}. {ejemplo['nombre']} ({ejemplo['dueno']})")
    
    print("\n=== SINCRONIZACIÓN COMPLETADA ===\n")
    print("✅ La tabla proveedores_meta ha sido actualizada con los datos de proveedores_duenos.")
    print("Ahora el formulario de agregar productos debería mostrar correctamente los proveedores.")

if __name__ == "__main__":
    sincronizar_proveedores_meta()