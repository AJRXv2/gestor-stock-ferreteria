import sqlite3

def duplicate_providers_for_both_owners():
    conn = sqlite3.connect('gestor_stock.db')
    cur = conn.cursor()
    
    # Obtener todos los proveedores que queremos duplicar
    cur.execute("SELECT id, nombre, dueno FROM proveedores_manual ORDER BY nombre")
    proveedores = cur.fetchall()
    
    duplicados = 0
    
    print("Proveedores actuales:")
    for p in proveedores:
        print(f"ID: {p[0]}, Nombre: {p[1]}, Dueño: {p[2]}")
    
    print("\n¿Qué proveedores quieres duplicar para que aparezcan en ambos dueños?")
    print("Ingresa el ID de cada proveedor separado por comas (ej. 2,3,5), o escribe 'todos' para duplicar todos:")
    
    seleccion = input("> ").strip().lower()
    
    proveedores_a_duplicar = []
    if seleccion == 'todos':
        proveedores_a_duplicar = proveedores
    else:
        ids = [int(id.strip()) for id in seleccion.split(',') if id.strip().isdigit()]
        for p in proveedores:
            if p[0] in ids:
                proveedores_a_duplicar.append(p)
    
    print(f"\nSe duplicarán {len(proveedores_a_duplicar)} proveedores:")
    for p in proveedores_a_duplicar:
        print(f"- {p[1]} (actualmente con dueño: {p[2]})")
    
    confirmacion = input("\n¿Confirmar? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Operación cancelada.")
        conn.close()
        return
    
    # Duplicar proveedores seleccionados
    for proveedor in proveedores_a_duplicar:
        id_proveedor, nombre, dueno_actual = proveedor
        
        # Determinar el otro dueño
        otro_dueno = 'ricky' if dueno_actual == 'ferreteria_general' else 'ferreteria_general'
        
        # Verificar si ya existe para el otro dueño
        cur.execute("SELECT id FROM proveedores_manual WHERE nombre = ? AND dueno = ?", (nombre, otro_dueno))
        existe = cur.fetchone()
        
        if not existe:
            # Crear el duplicado para el otro dueño
            cur.execute("INSERT INTO proveedores_manual (nombre, dueno) VALUES (?, ?)", (nombre, otro_dueno))
            duplicados += 1
            print(f"✅ Duplicado: '{nombre}' ahora también está disponible para '{otro_dueno}'")
        else:
            print(f"ℹ️ '{nombre}' ya estaba disponible para '{otro_dueno}'")
    
    conn.commit()
    
    # Verificar resultados finales
    cur.execute("SELECT dueno, COUNT(*) FROM proveedores_manual GROUP BY dueno")
    print("\nResultado final por dueño:")
    for row in cur.fetchall():
        print(f'Dueño: {row[0]}, Cantidad: {row[1]}')
    
    print(f"\nTotal de proveedores duplicados: {duplicados}")
    print("Ahora estos proveedores aparecerán en las listas de ambos dueños.")
    
    conn.close()

if __name__ == "__main__":
    print("Este script duplica proveedores para que aparezcan en ambos dueños (ricky y ferreteria_general)")
    duplicate_providers_for_both_owners()