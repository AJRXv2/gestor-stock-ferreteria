import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('gestor_stock.db')
cur = conn.cursor()

# Asignar proveedores a Ricky
cur.execute("UPDATE proveedores_manual SET dueno = 'ricky' WHERE nombre IN ('Berger', 'BremenTools', 'Cachan', 'Chiesa', 'Crossmaster') AND dueno IS NULL")
ricky_count = cur.rowcount
print(f'Proveedores asignados a Ricky: {ricky_count}')

# Asignar otros proveedores a Ferretería General
cur.execute("UPDATE proveedores_manual SET dueno = 'ferreteria_general' WHERE dueno IS NULL")
fg_count = cur.rowcount
print(f'Proveedores asignados a Ferretería General: {fg_count}')

# Guardar cambios
conn.commit()

# Verificar resultados
cur.execute("SELECT dueno, COUNT(*) FROM proveedores_manual GROUP BY dueno")
for row in cur.fetchall():
    print(f'Dueño: {row[0]}, Cantidad: {row[1]}')

cur.execute("SELECT id, nombre, dueno FROM proveedores_manual ORDER BY dueno, nombre")
print("\nLista de proveedores:")
for row in cur.fetchall():
    print(f'ID: {row[0]}, Nombre: {row[1]}, Dueño: {row[2]}')

conn.close()