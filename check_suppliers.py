import sqlite3

conn = sqlite3.connect('gestor_stock.db')
cursor = conn.cursor()

# Get all suppliers for ferreteria_general
cursor.execute("SELECT * FROM proveedores_manual WHERE dueno='ferreteria_general'")
rows = cursor.fetchall()
print("Suppliers for ferreteria_general:")
for row in rows:
    print(row)

# Get all suppliers for ricky
cursor.execute("SELECT * FROM proveedores_manual WHERE dueno='ricky'")
rows = cursor.fetchall()
print("\nSuppliers for ricky:")
for row in rows:
    print(row)

conn.close()