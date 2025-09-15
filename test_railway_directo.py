#!/usr/bin/env python3
"""
Script para probar directamente en Railway
"""

import requests
import json

def test_railway_directo():
    """Prueba directamente en Railway"""
    
    print("🔍 PROBANDO DIRECTAMENTE EN RAILWAY")
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
                
                # Verificar consultas específicas
                consultas = data.get('consultas', {})
                print(f"   Consultas disponibles: {list(consultas.keys())}")
                
                # Verificar búsqueda exacta
                if 'busqueda_exacta' in consultas:
                    busqueda = consultas['busqueda_exacta']
                    print(f"   Búsqueda exacta: {busqueda}")
                
                # Verificar proveedores
                if 'proveedores_muestra' in consultas:
                    proveedores = consultas['proveedores_muestra']
                    print(f"   Proveedores en DB: {len(proveedores)}")
                    for prov in proveedores:
                        if 'chiesa' in prov.get('nombre', '').lower():
                            print(f"     - Chiesa encontrado: {prov}")
                
            except Exception as e:
                print(f"   Error parseando JSON: {e}")
                print(f"   Respuesta: {response.text[:300]}...")
        
        # Probar endpoint de búsqueda específico
        print("\n🔍 Probando endpoint de búsqueda específico...")
        
        # Simular la búsqueda que debería funcionar
        url_busqueda = f"{base_url}/agregar_producto"
        params = {
            'busqueda_excel': 'CARBG7202',
            'solo_ricky': '1'
        }
        
        response = requests.get(url_busqueda, params=params, timeout=10)
        print(f"✅ Búsqueda general: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("   ✅ Producto encontrado en búsqueda general")
        else:
            print("   ❌ Producto NO encontrado en búsqueda general")
        
        # Probar búsqueda específica por proveedor manual
        print("\n🔍 Probando búsqueda específica por proveedor manual...")
        params_manual = {
            'proveedor_excel_ricky': 'manual_9_ricky',
            'busqueda_excel': 'CARBG7202',
            'solo_ricky': '1'
        }
        
        response = requests.get(url_busqueda, params=params_manual, timeout=10)
        print(f"✅ Búsqueda manual: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("   ✅ Producto encontrado en búsqueda manual")
        else:
            print("   ❌ Producto NO encontrado en búsqueda manual")
        
        # Verificar si hay algún error en la respuesta
        if response.status_code == 200:
            if "error" in response.text.lower() or "exception" in response.text.lower():
                print("   ⚠️ Posible error en la respuesta")
                # Buscar líneas con error
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if "error" in line.lower() or "exception" in line.lower():
                        print(f"     Línea {i}: {line.strip()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_railway_directo()

