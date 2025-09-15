import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('gestor_stock.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verificar cuántos proveedores hay por dueño
print("=== CONTEO DE PROVEEDORES POR DUEÑO ===")
cursor.execute("SELECT pd.dueno, COUNT(*) FROM proveedores_duenos pd GROUP BY pd.dueno")
rows = cursor.fetchall()
for row in rows:
    print(f"Dueño: {row[0]} - Proveedores: {row[1]}")

# Listar los proveedores por dueño
print("\n=== LISTA DE PROVEEDORES POR DUEÑO ===")
cursor.execute("""
    SELECT p.nombre, pd.dueno 
    FROM proveedores_manual p
    JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
    ORDER BY pd.dueno, p.nombre
""")
rows = cursor.fetchall()
current_dueno = None
for row in rows:
    if current_dueno != row['dueno']:
        current_dueno = row['dueno']
        print(f"\n{current_dueno.upper()}:")
    print(f"  - {row['nombre']}")

# Mostrar estructura de la tabla proveedores_duenos
print("\n=== ESTRUCTURA DE LA TABLA PROVEEDORES_DUENOS ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='proveedores_duenos'")
row = cursor.fetchone()
if row:
    print(row[0])
else:
    print("Tabla no encontrada")

# Verificar si hay dueños registrados en el sistema
print("\n=== DUEÑOS REGISTRADOS EN EL SISTEMA ===")
cursor.execute("SELECT DISTINCT dueno FROM proveedores_duenos")
rows = cursor.fetchall()
for row in rows:
    print(f"- {row['dueno']}")

# Verificar si hay proveedores sin asociar a dueños
print("\n=== PROVEEDORES SIN ASOCIAR A DUEÑOS ===")
cursor.execute("""
    SELECT p.id, p.nombre
    FROM proveedores_manual p
    WHERE NOT EXISTS (
        SELECT 1 FROM proveedores_duenos pd 
        WHERE pd.proveedor_id = p.id
    )
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"- ID: {row['id']}, Nombre: {row['nombre']}")
else:
    print("No hay proveedores sin asociar")

# Cerrar la conexión
conn.close()