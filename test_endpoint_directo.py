#!/usr/bin/env python3
"""
Script para probar el endpoint de búsqueda directamente
"""

import requests
import json

def test_endpoint_directo():
    """Prueba el endpoint de búsqueda directamente"""
    
    print("🔍 PROBANDO ENDPOINT DE BÚSQUEDA DIRECTO")
    print("=" * 50)
    
    try:
        base_url = "https://ferreteriacasapauluk.up.railway.app"
        
        # Probar endpoint de diagnóstico
        print("🔍 Probando endpoint de diagnóstico...")
        url_diagnostico = f"{base_url}/diagnostico_railway"
        response = requests.get(url_diagnostico, timeout=10)
        print(f"✅ Diagnóstico: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Ambiente: {data.get('ambiente', 'No disponible')}")
                print(f"   Consultas: {data.get('consultas', {})}")
            except:
                print(f"   Respuesta: {response.text[:200]}...")
        
        # Probar endpoint de búsqueda AJAX si existe
        print("\n🔍 Probando endpoint de búsqueda AJAX...")
        url_ajax = f"{base_url}/buscar_productos_ajax"
        
        # Datos para la búsqueda
        data = {
            'termino': 'CARBG7202',
            'proveedor_filtro': '',
            'solo_ricky': '1'
        }
        
        response = requests.post(url_ajax, data=data, timeout=10)
        print(f"✅ Búsqueda AJAX: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Resultado: {result}")
            except:
                print(f"   Respuesta: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint_directo()

