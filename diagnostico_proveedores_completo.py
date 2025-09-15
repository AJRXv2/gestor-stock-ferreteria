"""
Script para diagnosticar el estado de los proveedores y sus asociaciones con dueños.
"""
import sqlite3
import json
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

def diagnosticar_proveedores():
    """Ejecuta diagnóstico completo de proveedores."""
    print("\n=== DIAGNÓSTICO DE PROVEEDORES ===\n")
    
    # 1. Verificar tabla de proveedores_manual
    prov_manual = db_query("SELECT * FROM proveedores_manual", fetch=True)
    print(f"1. Total de proveedores en proveedores_manual: {len(prov_manual)}")
    
    # 2. Verificar tabla de relaciones proveedor-dueño
    relaciones = db_query("SELECT * FROM proveedores_duenos", fetch=True)
    print(f"2. Total de relaciones en proveedores_duenos: {len(relaciones)}")
    
    # 3. Verificar proveedores de ferreteria_general
    fg_provs = db_query("""
    SELECT p.id, p.nombre 
    FROM proveedores_manual p
    JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    WHERE pd.dueno = 'ferreteria_general'
    """, fetch=True)
    print(f"3. Proveedores asociados a ferreteria_general: {len(fg_provs)}")
    for p in fg_provs:
        print(f"   - ID: {p['id']}, Nombre: {p['nombre']}")
    
    # 4. Verificar proveedores de ricky
    ricky_provs = db_query("""
    SELECT p.id, p.nombre 
    FROM proveedores_manual p
    JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    WHERE pd.dueno = 'ricky'
    """, fetch=True)
    print(f"\n4. Proveedores asociados a ricky: {len(ricky_provs)}")
    for p in ricky_provs:
        print(f"   - ID: {p['id']}, Nombre: {p['nombre']}")
    
    # 5. Verificar proveedores sin asociación a dueño
    sin_dueno = db_query("""
    SELECT p.id, p.nombre 
    FROM proveedores_manual p
    LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    WHERE pd.proveedor_id IS NULL
    """, fetch=True)
    print(f"\n5. Proveedores SIN asociación a dueño: {len(sin_dueno)}")
    for p in sin_dueno:
        print(f"   - ID: {p['id']}, Nombre: {p['nombre']}")
    
    # 6. Verificar proveedores con más de un dueño
    multi_dueno = db_query("""
    SELECT p.id, p.nombre, COUNT(pd.dueno) as num_duenos, GROUP_CONCAT(pd.dueno) as duenos
    FROM proveedores_manual p
    JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    GROUP BY p.id
    HAVING COUNT(pd.dueno) > 1
    """, fetch=True)
    print(f"\n6. Proveedores con MÚLTIPLES dueños: {len(multi_dueno)}")
    for p in multi_dueno:
        print(f"   - ID: {p['id']}, Nombre: {p['nombre']}, Dueños: {p['duenos']}")
    
    # 7. Verificar si hay relaciones a proveedores que no existen
    huerfanos = db_query("""
    SELECT pd.proveedor_id, pd.dueno
    FROM proveedores_duenos pd
    LEFT JOIN proveedores_manual p ON p.id = pd.proveedor_id
    WHERE p.id IS NULL
    """, fetch=True)
    print(f"\n7. Relaciones a proveedores inexistentes: {len(huerfanos)}")
    for h in huerfanos:
        print(f"   - ID Proveedor: {h['proveedor_id']}, Dueño: {h['dueno']}")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===\n")

if __name__ == "__main__":
    diagnosticar_proveedores()