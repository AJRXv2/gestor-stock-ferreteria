import sqlite3

def migrate_providers():
    conn = sqlite3.connect('gestor_stock.db')
    cur = conn.cursor()
    
    # Obtener todos los proveedores
    cur.execute("SELECT id, nombre, dueno FROM proveedores_manual")
    proveedores = cur.fetchall()
    
    # Llenar la tabla auxiliar
    for proveedor in proveedores:
        proveedor_id, nombre, dueno = proveedor
        if dueno:
            cur.execute("INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", 
                       (proveedor_id, dueno))
    
    conn.commit()
    
    # Verificar resultados
    cur.execute("SELECT COUNT(*) FROM proveedores_duenos")
    count = cur.fetchone()[0]
    print(f"Migrados {count} relaciones proveedor-dueño")
    
    conn.close()

def update_providers_owners():
    conn = sqlite3.connect('gestor_stock.db')
    cur = conn.cursor()
    
    # Mostrar proveedores actuales
    cur.execute("""
        SELECT p.id, p.nombre, GROUP_CONCAT(pd.dueno, ', ') as duenos
        FROM proveedores_manual p
        LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        GROUP BY p.id
        ORDER BY p.nombre
    """)
    
    proveedores = cur.fetchall()
    print("\nProveedores actuales y sus dueños:")
    for p in proveedores:
        print(f"ID: {p[0]}, Nombre: {p[1]}, Dueños: {p[2] or 'Ninguno'}")
    
    print("\n¿Qué proveedores quieres que estén disponibles para ambos dueños?")
    print("Ingresa los IDs separados por comas, o 'todos' para todos:")
    
    seleccion = input("> ").strip().lower()
    
    proveedores_a_actualizar = []
    if seleccion == 'todos':
        proveedores_a_actualizar = proveedores
    else:
        ids = [int(id.strip()) for id in seleccion.split(',') if id.strip().isdigit()]
        for p in proveedores:
            if p[0] in ids:
                proveedores_a_actualizar.append(p)
    
    print(f"\nActualizando {len(proveedores_a_actualizar)} proveedores:")
    for p in proveedores_a_actualizar:
        print(f"- {p[1]}")
    
    confirmacion = input("\n¿Confirmar? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Operación cancelada.")
        conn.close()
        return
    
    # Actualizar para que estén disponibles para ambos dueños
    for p in proveedores_a_actualizar:
        cur.execute("INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ricky')", (p[0],))
        cur.execute("INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, 'ferreteria_general')", (p[0],))
    
    conn.commit()
    
    # Verificar estado final
    cur.execute("""
        SELECT p.id, p.nombre, GROUP_CONCAT(pd.dueno, ', ') as duenos
        FROM proveedores_manual p
        LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        GROUP BY p.id
        ORDER BY p.nombre
    """)
    
    proveedores = cur.fetchall()
    print("\nEstado final de los proveedores:")
    for p in proveedores:
        print(f"ID: {p[0]}, Nombre: {p[1]}, Dueños: {p[2] or 'Ninguno'}")
    
    conn.close()
    
    print("\nAhora debemos modificar la función obtener_proveedores_por_dueno en gestor.py")
    print("para que use la nueva tabla proveedores_duenos en lugar de la columna dueno")
    print("en la tabla proveedores_manual.")

if __name__ == "__main__":
    migrate_providers()
    
    print("\nAhora vamos a permitir que asignes proveedores a ambos dueños:")
    update_providers_owners()