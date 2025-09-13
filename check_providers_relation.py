import sqlite3

def check_providers_relation():
    """Verifica la relación de proveedores y dueños"""
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== Proveedores con sus dueños ===")
    cursor.execute("""
        SELECT pm.id, pm.nombre, pd.dueno
        FROM proveedores_manual pm
        JOIN proveedores_duenos pd ON pm.id = pd.proveedor_id
        ORDER BY pm.nombre, pd.dueno
    """)
    
    results = cursor.fetchall()
    
    # Agrupar por nombre de proveedor para ver claramente quién tiene cuáles dueños
    providers_by_name = {}
    
    for row in results:
        provider_id = row['id']
        provider_name = row['nombre']
        dueno = row['dueno']
        
        if provider_name not in providers_by_name:
            providers_by_name[provider_name] = {'id': provider_id, 'duenos': []}
        
        providers_by_name[provider_name]['duenos'].append(dueno)
    
    # Mostrar resultados
    for name, data in providers_by_name.items():
        duenos_str = ", ".join(data['duenos'])
        print(f"Proveedor: '{name}' (ID: {data['id']}) - Dueños: {duenos_str}")
    
    print("\n=== Estadísticas ===")
    print(f"Total de proveedores: {len(providers_by_name)}")
    
    with_both = sum(1 for data in providers_by_name.values() if set(['ricky', 'ferreteria_general']).issubset(set(data['duenos'])))
    only_ricky = sum(1 for data in providers_by_name.values() if data['duenos'] == ['ricky'])
    only_fg = sum(1 for data in providers_by_name.values() if data['duenos'] == ['ferreteria_general'])
    
    print(f"Con ambos dueños: {with_both}")
    print(f"Solo Ricky: {only_ricky}")
    print(f"Solo Ferretería General: {only_fg}")
    
    print("\n=== Proveedores específicos ===")
    for name in ['Hoteche', 'Sorbalok']:
        if name in providers_by_name:
            duenos_str = ", ".join(providers_by_name[name]['duenos'])
            print(f"Proveedor: '{name}' - Dueños: {duenos_str}")
        else:
            print(f"Proveedor: '{name}' - No encontrado")
    
    conn.close()

if __name__ == "__main__":
    check_providers_relation()