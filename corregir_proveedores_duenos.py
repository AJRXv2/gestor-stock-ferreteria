"""
Script para corregir el problema de carga de proveedores.
Este script asegura que cada proveedor esté correctamente asociado a su dueño.
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

def corregir_proveedores():
    """Corrige las relaciones entre proveedores y dueños."""
    print("\n=== CORRECCIÓN DE PROVEEDORES Y DUEÑOS ===\n")
    
    # 1. Limpiar cualquier relación huérfana
    huerfanos = db_query("""
    DELETE FROM proveedores_duenos 
    WHERE proveedor_id IN (
        SELECT pd.proveedor_id
        FROM proveedores_duenos pd
        LEFT JOIN proveedores_manual p ON p.id = pd.proveedor_id
        WHERE p.id IS NULL
    )
    """)
    print("1. Relaciones huérfanas eliminadas.")
    
    # 2. Obtener todos los proveedores
    proveedores = db_query("SELECT id, nombre FROM proveedores_manual", fetch=True)
    print(f"2. Total de proveedores: {len(proveedores)}")
    
    # 3. Para cada proveedor, verificar si tiene relación con algún dueño
    for p in proveedores:
        relaciones = db_query(
            "SELECT dueno FROM proveedores_duenos WHERE proveedor_id = ?", 
            (p['id'],), 
            fetch=True
        )
        
        if not relaciones:
            # Si no tiene relación, asignar a ferreteria_general por defecto
            print(f"   - Proveedor '{p['nombre']}' (ID: {p['id']}) no tiene dueño. Asignando a ferreteria_general.")
            db_query(
                "INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)",
                (p['id'], 'ferreteria_general')
            )
    
    # 4. Verificar que todos los proveedores tienen al menos una relación
    sin_dueno = db_query("""
    SELECT p.id, p.nombre 
    FROM proveedores_manual p
    LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    WHERE pd.proveedor_id IS NULL
    """, fetch=True)
    
    if sin_dueno:
        print(f"\n⚠️ Aún hay {len(sin_dueno)} proveedores sin dueño:")
        for p in sin_dueno:
            print(f"   - {p['nombre']} (ID: {p['id']})")
    else:
        print("\n✅ Todos los proveedores tienen al menos un dueño asignado.")
    
    # 5. Estadísticas finales
    fg_count = db_query(
        "SELECT COUNT(*) as count FROM proveedores_duenos WHERE dueno = 'ferreteria_general'", 
        fetch=True
    )[0]['count']
    
    ricky_count = db_query(
        "SELECT COUNT(*) as count FROM proveedores_duenos WHERE dueno = 'ricky'", 
        fetch=True
    )[0]['count']
    
    total_provs = db_query(
        "SELECT COUNT(*) as count FROM proveedores_manual", 
        fetch=True
    )[0]['count']
    
    print(f"\nEstadísticas:")
    print(f"- Total de proveedores: {total_provs}")
    print(f"- Proveedores de ferreteria_general: {fg_count}")
    print(f"- Proveedores de ricky: {ricky_count}")
    
    print("\n=== CORRECCIÓN COMPLETADA ===\n")

if __name__ == "__main__":
    corregir_proveedores()