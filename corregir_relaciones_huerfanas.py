"""
Script para corregir relaciones huérfanas de proveedores-dueños.
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

def corregir_relaciones_huerfanas():
    """Elimina relaciones huérfanas y corrige problemas de proveedores."""
    print("\n=== CORRECCIÓN DE RELACIONES HUÉRFANAS ===\n")
    
    # 1. Identificar relaciones huérfanas
    huerfanos = db_query("""
    SELECT pd.proveedor_id, pd.dueno
    FROM proveedores_duenos pd
    LEFT JOIN proveedores_manual p ON p.id = pd.proveedor_id
    WHERE p.id IS NULL
    """, fetch=True)
    
    if not huerfanos:
        print("No se encontraron relaciones huérfanas. ¡Todo en orden!")
        return
    
    print(f"Se encontraron {len(huerfanos)} relaciones huérfanas:")
    for h in huerfanos:
        print(f"   - ID Proveedor: {h['proveedor_id']}, Dueño: {h['dueno']}")
    
    # 2. Eliminar relaciones huérfanas
    eliminados = db_query("""
    DELETE FROM proveedores_duenos 
    WHERE proveedor_id IN (
        SELECT pd.proveedor_id
        FROM proveedores_duenos pd
        LEFT JOIN proveedores_manual p ON p.id = pd.proveedor_id
        WHERE p.id IS NULL
    )
    """)
    
    print(f"\nSe han eliminado las relaciones huérfanas.")
    
    # 3. Verificar proveedores sin relación
    sin_dueno = db_query("""
    SELECT p.id, p.nombre 
    FROM proveedores_manual p
    LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    WHERE pd.proveedor_id IS NULL
    """, fetch=True)
    
    if sin_dueno:
        print(f"\nSe encontraron {len(sin_dueno)} proveedores sin asociación a dueño:")
        for p in sin_dueno:
            print(f"   - ID: {p['id']}, Nombre: {p['nombre']}")
            
            # Asignar automáticamente a ferreteria_general como valor predeterminado
            db_query("""
            INSERT INTO proveedores_duenos (proveedor_id, dueno)
            VALUES (?, 'ferreteria_general')
            """, (p['id'],))
            print(f"   ✅ Asignado automáticamente a 'ferreteria_general'")
    
    print("\n=== CORRECCIÓN COMPLETADA ===\n")

if __name__ == "__main__":
    corregir_relaciones_huerfanas()