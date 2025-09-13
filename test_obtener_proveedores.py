import requests
import json

def test_obtener_proveedores():
    """Test para la función obtener_proveedores_por_dueno"""
    print("\n=== Test para obtener_proveedores_por_dueno ===")
    
    # Endpoints - usando directamente la IP local
    url_debug = 'http://192.168.0.180:5000/debug_obtener_proveedores_por_dueno'
    
    # Verificar para Ricky
    print("\nVerificando proveedores para Ricky...")
    try:
        # Usar el endpoint de debug que no requiere autenticación
        response = requests.get(
            f'{url_debug}/ricky',
            headers={'Content-Type': 'application/json'}
        )
        

        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success', False):
                proveedores = data.get('proveedores', [])
                print(f"Proveedores encontrados para Ricky: {len(proveedores)}")
                # Verificar algunos proveedores específicos
                for p in ['Hoteche', 'Sorbalok']:
                    if p in proveedores:
                        print(f"✅ '{p}' encontrado para Ricky")
                    else:
                        print(f"❌ '{p}' NO encontrado para Ricky")
            else:
                print(f"❌ ERROR en la respuesta: {data.get('msg', 'Unknown')}")
        else:
            print(f"❌ ERROR: API respondió con código {response.status_code}")
            print(f"Contenido: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: Excepción al llamar API para Ricky: {str(e)}")
    
    # Verificar para Ferretería General
    print("\nVerificando proveedores para Ferretería General...")
    try:
        # Usar el endpoint de debug que no requiere autenticación
        response = requests.get(
            f'{url_debug}/ferreteria_general',
            headers={'Content-Type': 'application/json'}
        )
        

        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success', False):
                proveedores = data.get('proveedores', [])
                print(f"Proveedores encontrados para Ferretería General: {len(proveedores)}")
                # Verificar algunos proveedores específicos
                for p in ['Hoteche', 'Sorbalok']:
                    if p in proveedores:
                        print(f"✅ '{p}' encontrado para Ferretería General")
                    else:
                        print(f"❌ '{p}' NO encontrado para Ferretería General")
            else:
                print(f"❌ ERROR en la respuesta: {data.get('msg', 'Unknown')}")
        else:
            print(f"❌ ERROR: API respondió con código {response.status_code}")
            print(f"Contenido: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: Excepción al llamar API para Ferretería General: {str(e)}")

if __name__ == "__main__":
    test_obtener_proveedores()