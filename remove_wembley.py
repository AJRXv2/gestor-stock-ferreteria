import sqlite3

def main():
    conn = sqlite3.connect('gestor_stock.db')
    cursor = conn.cursor()

    # 1. Check if WEMBLEY exists
    cursor.execute("SELECT id FROM proveedores_manual WHERE nombre='WEMBLEY'")
    wembley_id = cursor.fetchone()
    
    if wembley_id:
        wembley_id = wembley_id[0]
        print(f"Found WEMBLEY with ID: {wembley_id}")
        
        # 2. Delete WEMBLEY
        cursor.execute("DELETE FROM proveedores_manual WHERE id=?", (wembley_id,))
        conn.commit()
        print(f"Deleted WEMBLEY (ID: {wembley_id}) from the database")
    else:
        print("WEMBLEY not found in the database")

    # 3. Verify the deletion
    cursor.execute("SELECT * FROM proveedores_manual WHERE dueno='ferreteria_general'")
    ferreteria_suppliers = cursor.fetchall()
    print("\nSuppliers for ferreteria_general after deletion:")
    for supplier in ferreteria_suppliers:
        print(supplier)

    conn.close()

if __name__ == "__main__":
    main()