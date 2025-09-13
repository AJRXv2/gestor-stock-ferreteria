import sqlite3

def add_and_check_provider():
    """Adds a test provider to both owners and checks if it appears for both."""
    print("\n=== Test de agregar proveedor a ambos dueños ===")
    
    # Configuración inicial
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    test_provider = "ProveedorTest" + "123"  # Nombre único para pruebas
    
    # Limpiar cualquier proveedor de prueba anterior
    print(f"Eliminando cualquier proveedor anterior con nombre '{test_provider}'...")
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id IN (SELECT id FROM proveedores_manual WHERE nombre=?)", (test_provider,))
    cursor.execute("DELETE FROM proveedores_meta WHERE nombre=?", (test_provider,))  # Para compatibilidad
    cursor.execute("DELETE FROM proveedores_manual WHERE nombre=?", (test_provider,))
    conn.commit()
    print("Limpieza completada.")
    
    # Paso 1: Insertar nuevo proveedor en la tabla principal
    print(f"Creando nuevo proveedor: '{test_provider}'...")
    cursor.execute("INSERT INTO proveedores_manual (nombre) VALUES (?)", (test_provider,))
    proveedor_id = cursor.lastrowid
    print(f"Proveedor creado con ID: {proveedor_id}")
    
    # Paso 2: Asociar a ambos dueños
    print("Asociando a ambos dueños...")
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ricky'))
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ferreteria_general'))
    
    # También en la tabla legacy para compatibilidad
    cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES (?, ?)", (test_provider, 'ricky'))
    cursor.execute("INSERT INTO proveedores_meta (nombre, dueno) VALUES (?, ?)", (test_provider, 'ferreteria_general'))
    
    conn.commit()
    print("Asociaciones creadas.")
    
    # Paso 3: Verificar si el proveedor aparece para Ricky
    print("\nVerificando si el proveedor aparece para Ricky...")
    cursor.execute("""
        SELECT p.nombre 
        FROM proveedores_manual p
        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        WHERE pd.dueno = 'ricky' AND p.nombre = ?
    """, (test_provider,))
    result_ricky = cursor.fetchall()
    
    if result_ricky:
        print(f"✅ ÉXITO: Proveedor '{test_provider}' encontrado para Ricky")
    else:
        print(f"❌ ERROR: Proveedor '{test_provider}' NO encontrado para Ricky")
    
    # Paso 4: Verificar si el proveedor aparece para Ferretería General
    print("\nVerificando si el proveedor aparece para Ferretería General...")
    cursor.execute("""
        SELECT p.nombre 
        FROM proveedores_manual p
        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        WHERE pd.dueno = 'ferreteria_general' AND p.nombre = ?
    """, (test_provider,))
    result_fg = cursor.fetchall()
    
    if result_fg:
        print(f"✅ ÉXITO: Proveedor '{test_provider}' encontrado para Ferretería General")
    else:
        print(f"❌ ERROR: Proveedor '{test_provider}' NO encontrado para Ferretería General")
    
    # Verificar también la tabla legacy proveedores_meta
    print("\nVerificando tabla legacy proveedores_meta para Ricky...")
    cursor.execute("""
        SELECT nombre FROM proveedores_meta
        WHERE dueno = 'ricky' AND nombre = ?
    """, (test_provider,))
    legacy_ricky = cursor.fetchall()
    
    if legacy_ricky:
        print(f"✅ ÉXITO: Proveedor '{test_provider}' encontrado en tabla legacy para Ricky")
    else:
        print(f"❌ ERROR: Proveedor '{test_provider}' NO encontrado en tabla legacy para Ricky")
    
    print("\nVerificando tabla legacy proveedores_meta para Ferretería General...")
    cursor.execute("""
        SELECT nombre FROM proveedores_meta
        WHERE dueno = 'ferreteria_general' AND nombre = ?
    """, (test_provider,))
    legacy_fg = cursor.fetchall()
    
    if legacy_fg:
        print(f"✅ ÉXITO: Proveedor '{test_provider}' encontrado en tabla legacy para Ferretería General")
    else:
        print(f"❌ ERROR: Proveedor '{test_provider}' NO encontrado en tabla legacy para Ferretería General")
    
    # Limpiar
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id = ?", (proveedor_id,))
    cursor.execute("DELETE FROM proveedores_meta WHERE nombre = ?", (test_provider,))  # Para compatibilidad
    cursor.execute("DELETE FROM proveedores_manual WHERE id = ?", (proveedor_id,))
    conn.commit()
    conn.close()
    
    print("\nTest completado y limpieza realizada.")

if __name__ == "__main__":
    add_and_check_provider()