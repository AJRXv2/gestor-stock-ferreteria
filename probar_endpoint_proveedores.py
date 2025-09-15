"""
Script para probar el endpoint de obtener proveedores por dueño.
"""
import requests
import json

def probar_endpoint():
    """Prueba el endpoint para obtener proveedores por dueño."""
    print("\n=== PRUEBA DE ENDPOINT DE PROVEEDORES ===\n")
    
    url = "http://127.0.0.1:5000/obtener_proveedores_por_dueno_test"
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Probar con ferreteria_general
    print("1. Probando para dueño: ferreteria_general")
    payload = {"dueno": "ferreteria_general"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"✅ Se encontraron {len(data.get('proveedores', []))} proveedores:")
            for i, prov in enumerate(data.get('proveedores', []), 1):
                print(f"   {i}. {prov}")
        else:
            print(f"❌ Error: {data.get('msg', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Error al realizar la petición: {str(e)}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Probar con ricky
    print("2. Probando para dueño: ricky")
    payload = {"dueno": "ricky"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"✅ Se encontraron {len(data.get('proveedores', []))} proveedores:")
            for i, prov in enumerate(data.get('proveedores', []), 1):
                print(f"   {i}. {prov}")
        else:
            print(f"❌ Error: {data.get('msg', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Error al realizar la petición: {str(e)}")
    
    print("\n=== PRUEBA COMPLETADA ===\n")

if __name__ == "__main__":
    print("Asegúrate de que la aplicación Flask esté ejecutándose en http://127.0.0.1:5000/")
    print("Presiona Enter para continuar o Ctrl+C para cancelar...")
    input()
    probar_endpoint()