import sqlite3

def verificar_sorbalok():
    """Verifica si el proveedor Sorbalok existe en la base de datos y está asociado a los dueños"""
    
    print("\n=== Verificación de Sorbalok en la base de datos ===")
    
    # Conectar a la base de datos
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verificar si existe en proveedores_manual
    cursor.execute("SELECT id, nombre FROM proveedores_manual WHERE nombre LIKE '%Sorbalok%'")
    proveedor = cursor.fetchone()
    
    if not proveedor:
        print("❌ ERROR: Sorbalok no existe en la tabla proveedores_manual")
        print("Vamos a intentar crearlo y asociarlo a ambos dueños:")
        
        # Crear proveedor
        cursor.execute("INSERT INTO proveedores_manual (nombre) VALUES ('Sorbalok')")
        proveedor_id = cursor.lastrowid
        
        # Asociar a ambos dueños
        cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ricky')", (proveedor_id,))
        cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ferreteria_general')", (proveedor_id,))
        
        # Legacy
        cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES ('Sorbalok', 'ricky')")
        cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES ('Sorbalok', 'ferreteria_general')")
        
        conn.commit()
        print(f"✅ Sorbalok creado con ID {proveedor_id} y asociado a ambos dueños")
        
    else:
        proveedor_id = proveedor['id']
        print(f"✅ Sorbalok existe en proveedores_manual con ID: {proveedor_id}")
        
        # Verificar asociaciones en proveedores_duenos
        cursor.execute("SELECT dueno FROM proveedores_duenos WHERE proveedor_id = ?", (proveedor_id,))
        duenos = [row['dueno'] for row in cursor.fetchall()]
        
        print(f"Dueños asociados en proveedores_duenos: {duenos}")
        
        if 'ricky' not in duenos:
            print("❌ Falta asociación con Ricky. Agregando...")
            cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ricky')", (proveedor_id,))
            conn.commit()
            print("✅ Asociación con Ricky agregada")
            
        if 'ferreteria_general' not in duenos:
            print("❌ Falta asociación con Ferretería General. Agregando...")
            cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ferreteria_general')", (proveedor_id,))
            conn.commit()
            print("✅ Asociación con Ferretería General agregada")
            
        # Verificar asociaciones en proveedores_meta (legacy)
        cursor.execute("SELECT dueno FROM proveedores_meta WHERE LOWER(nombre) LIKE LOWER('%Sorbalok%')")
        duenos_legacy = [row['dueno'] for row in cursor.fetchall()]
        
        print(f"Dueños asociados en proveedores_meta (legacy): {duenos_legacy}")
        
        if 'ricky' not in duenos_legacy:
            print("❌ Falta asociación legacy con Ricky. Agregando...")
            cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES ('Sorbalok', 'ricky')")
            conn.commit()
            print("✅ Asociación legacy con Ricky agregada")
            
        if 'ferreteria_general' not in duenos_legacy:
            print("❌ Falta asociación legacy con Ferretería General. Agregando...")
            cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES ('Sorbalok', 'ferreteria_general')")
            conn.commit()
            print("✅ Asociación legacy con Ferretería General agregada")
    
    # Verificación final
    print("\n=== Verificación final ===")
    cursor.execute("""
        SELECT p.nombre, pd.dueno
        FROM proveedores_manual p
        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        WHERE p.nombre LIKE '%Sorbalok%'
        ORDER BY pd.dueno
    """)
    
    rows = cursor.fetchall()
    if rows:
        print("Sorbalok está asociado a los siguientes dueños:")
        for row in rows:
            print(f"  - {row['dueno']}")
    else:
        print("❌ ERROR: No se encontró Sorbalok después de intentar crearlo/actualizarlo")
    
    conn.close()
    print("\nVerificación completada.")

if __name__ == "__main__":
    verificar_sorbalok()