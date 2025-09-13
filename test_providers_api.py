import sqlite3
import json
import requests

def test_providers_relation():
    """Prueba la relación de proveedores y dueños, y verifica la API"""
    print("\n=== Probando relación de proveedores y endpoint de API ===")
    
    # 1. Primero, verificar el estado actual de la tabla proveedores_duenos
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT pm.id, pm.nombre, pd.dueno
        FROM proveedores_manual pm
        JOIN proveedores_duenos pd ON pm.id = pd.proveedor_id
        WHERE pm.nombre = 'Test Provider'
        ORDER BY pm.nombre, pd.dueno
    """)
    
    results = cursor.fetchall()
    
    if results:
        print("Proveedor de prueba ya existe, limpiando...")
        cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id IN (SELECT id FROM proveedores_manual WHERE nombre = 'Test Provider')")
        cursor.execute("DELETE FROM proveedores_manual WHERE nombre = 'Test Provider'")
        conn.commit()
    
    # 2. Insertar un proveedor de prueba para ambos dueños
    print("\nInsertando proveedor de prueba para ambos dueños...")
    cursor.execute("INSERT INTO proveedores_manual (nombre) VALUES ('Test Provider')")
    proveedor_id = cursor.lastrowid
    
    # Asignar a ambos dueños
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ricky'))
    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)", (proveedor_id, 'ferreteria_general'))
    conn.commit()
    
    print(f"Proveedor de prueba creado con ID {proveedor_id}")
    
    # 3. Probar la API para cada dueño
    try:
        print("\nProbando API para Ricky...")
        try:
            response_ricky = requests.post(
                'http://localhost:5000/obtener_proveedores_por_dueno_test',
                json={'dueno': 'ricky'},
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response_ricky.status_code}")
            print(f"Response Content: {response_ricky.text[:200]}...")
            
            if response_ricky.status_code == 200:
                data_ricky = response_ricky.json()
                if data_ricky.get('success'):
                    proveedores_ricky = data_ricky.get('proveedores', [])
                    if 'Test Provider' in proveedores_ricky:
                        print("✅ Éxito: Test Provider aparece en la lista de Ricky")
                    else:
                        print("❌ Error: Test Provider NO aparece en la lista de Ricky")
                        print(f"Proveedores disponibles para Ricky: {proveedores_ricky}")
                else:
                    print(f"❌ Error en la respuesta: {data_ricky.get('msg', 'Desconocido')}")
            else:
                print(f"❌ Error en la API: {response_ricky.status_code}")
        except Exception as e:
            print(f"Excepción al probar API para Ricky: {e}")
        
        print("\nProbando API para Ferretería General...")
        try:
            response_fg = requests.post(
                'http://localhost:5000/obtener_proveedores_por_dueno_test',
                json={'dueno': 'ferreteria_general'},
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response_fg.status_code}")
            print(f"Response Content: {response_fg.text[:200]}...")
            
            if response_fg.status_code == 200:
                data_fg = response_fg.json()
                if data_fg.get('success'):
                    proveedores_fg = data_fg.get('proveedores', [])
                    if 'Test Provider' in proveedores_fg:
                        print("✅ Éxito: Test Provider aparece en la lista de Ferretería General")
                    else:
                        print("❌ Error: Test Provider NO aparece en la lista de Ferretería General")
                        print(f"Proveedores disponibles para FG: {proveedores_fg}")
                else:
                    print(f"❌ Error en la respuesta: {data_fg.get('msg', 'Desconocido')}")
            else:
                print(f"❌ Error en la API: {response_fg.status_code}")
        except Exception as e:
            print(f"Excepción al probar API para Ferretería General: {e}")
    
    except Exception as e:
        print(f"Error al probar API: {e}")
    
    # 4. Limpiar datos de prueba
    print("\nLimpiando datos de prueba...")
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id = ?", (proveedor_id,))
    cursor.execute("DELETE FROM proveedores_manual WHERE id = ?", (proveedor_id,))
    conn.commit()
    
    conn.close()
    print("Prueba completada.")

if __name__ == "__main__":
    test_providers_relation()
            )
            
            print(f"Status Code: {response_fg.status_code}")
            print(f"Response Headers: {response_fg.headers}")
            print(f"Response Content: {response_fg.text}")
            
            if response_fg.status_code == 200:
                data_fg = response_fg.json()
                if data_fg.get('success'):
                    proveedores_fg = data_fg.get('proveedores', [])
                    if 'Test Provider' in proveedores_fg:
                        print("✅ Éxito: Test Provider aparece en la lista de Ferretería General")
                    else:
                        print("❌ Error: Test Provider NO aparece en la lista de Ferretería General")
                        print(f"Proveedores disponibles para FG: {proveedores_fg}")
                else:
                    print(f"❌ Error en la respuesta: {data_fg.get('msg', 'Desconocido')}")
            else:
                print(f"❌ Error en la API: {response_fg.status_code}")
        except Exception as e:
            print(f"Excepción al probar API para Ferretería General: {e}")
        )
        
        if response_fg.status_code == 200:
            data_fg = response_fg.json()
            if data_fg.get('success'):
                proveedores_fg = data_fg.get('proveedores', [])
                if 'Test Provider' in proveedores_fg:
                    print("✅ Éxito: Test Provider aparece en la lista de Ferretería General")
                else:
                    print("❌ Error: Test Provider NO aparece en la lista de Ferretería General")
                    print(f"Proveedores disponibles para FG: {proveedores_fg}")
            else:
                print(f"❌ Error en la respuesta: {data_fg.get('msg', 'Desconocido')}")
        else:
            print(f"❌ Error en la API: {response_fg.status_code}")
    
    except Exception as e:
        print(f"Error al probar API: {e}")
    
    # 4. Limpiar datos de prueba
    print("\nLimpiando datos de prueba...")
    cursor.execute("DELETE FROM proveedores_duenos WHERE proveedor_id = ?", (proveedor_id,))
    cursor.execute("DELETE FROM proveedores_manual WHERE id = ?", (proveedor_id,))
    conn.commit()
    
    conn.close()
    print("Prueba completada.")

if __name__ == "__main__":
    test_providers_relation()