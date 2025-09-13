import sqlite3
import requests

def test_proveedores():
    """Test para verificar si la API de proveedores funciona correctamente"""
    print("\n=== Test de API de Proveedores ===")
    
    # Configuración inicial
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Limpiar cualquier proveedor de prueba anterior
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id IN (SELECT id FROM proveedores_manual WHERE nombre='Test Provider')")
    cursor.execute("DELETE FROM proveedores_manual WHERE nombre='Test Provider'")
    conn.commit()
    
    # Crear un nuevo proveedor de prueba
    cursor.execute("INSERT INTO proveedores_manual (nombre) VALUES ('Test Provider')")
    proveedor_id = cursor.lastrowid
    print(f"Proveedor de prueba creado con ID: {proveedor_id}")
    
    # Asociar a ambos dueños
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ricky'))
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ferreteria_general'))
    conn.commit()
    print("Proveedor asociado a ambos dueños")
    
    # Verificar API para Ricky
    print("\nVerificando API para Ricky...")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/obtener_proveedores_por_dueno_test',
            json={'dueno': 'ricky'},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                proveedores = data.get('proveedores', [])
                if 'Test Provider' in proveedores:
                    print("✅ ÉXITO: Test Provider encontrado en lista de Ricky")
                else:
                    print("❌ ERROR: Test Provider NO encontrado en lista de Ricky")
                    print(f"Proveedores encontrados: {proveedores}")
            else:
                print(f"❌ ERROR: Respuesta con error: {data.get('msg', 'Unknown')}")
        else:
            print(f"❌ ERROR: API respondió con código {response.status_code}")
            print(f"Contenido: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: Excepción al llamar API para Ricky: {str(e)}")
    
    # Verificar API para Ferretería General
    print("\nVerificando API para Ferretería General...")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/obtener_proveedores_por_dueno_test',
            json={'dueno': 'ferreteria_general'},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                proveedores = data.get('proveedores', [])
                if 'Test Provider' in proveedores:
                    print("✅ ÉXITO: Test Provider encontrado en lista de Ferretería General")
                else:
                    print("❌ ERROR: Test Provider NO encontrado en lista de Ferretería General")
                    print(f"Proveedores encontrados: {proveedores}")
            else:
                print(f"❌ ERROR: Respuesta con error: {data.get('msg', 'Unknown')}")
        else:
            print(f"❌ ERROR: API respondió con código {response.status_code}")
            print(f"Contenido: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: Excepción al llamar API para Ferretería General: {str(e)}")
    
    # Limpiar
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id = ?", (proveedor_id,))
    cursor.execute("DELETE FROM proveedores_manual WHERE id = ?", (proveedor_id,))
    conn.commit()
    conn.close()
    
    print("\nTest completado.")

if __name__ == "__main__":
    test_proveedores()