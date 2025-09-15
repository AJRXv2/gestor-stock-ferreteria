#!/usr/bin/env python3
"""
Script para verificar si el producto está en Railway
"""

import requests
import json

def verificar_producto_railway():
    """Verifica si el producto está en Railway"""
    
    print("🔍 VERIFICANDO PRODUCTO EN RAILWAY")
    print("=" * 50)
    
    try:
        base_url = "https://ferreteriacasapauluk.up.railway.app"
        
        # Probar endpoint de diagnóstico con más detalles
        print("🔍 Probando endpoint de diagnóstico detallado...")
        url_diagnostico = f"{base_url}/diagnostico_railway"
        response = requests.get(url_diagnostico, timeout=10)
        print(f"✅ Diagnóstico: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Ambiente: {data.get('ambiente', 'No disponible')}")
                
                # Verificar consultas específicas
                consultas = data.get('consultas', {})
                
                # Verificar búsqueda exacta de CARBG7202
                print("\n🔍 Verificando búsqueda exacta de CARBG7202...")
                if 'busqueda_exacta' in consultas:
                    busqueda = consultas['busqueda_exacta']
                    print(f"   Búsqueda exacta: {busqueda}")
                
                # Verificar proveedores
                print("\n🏢 Verificando proveedores...")
                if 'proveedores_muestra' in consultas:
                    proveedores = consultas['proveedores_muestra']
                    print(f"   Total proveedores: {len(proveedores)}")
                    for prov in proveedores:
                        print(f"     - ID: {prov.get('id')}, Nombre: '{prov.get('nombre')}', Dueño: {prov.get('dueno')}")
                
                # Verificar proveedores con dueños
                print("\n🏢 Verificando proveedores con dueños...")
                if 'proveedores_duenos_muestra' in consultas:
                    proveedores_duenos = consultas['proveedores_duenos_muestra']
                    print(f"   Total proveedores con dueños: {len(proveedores_duenos)}")
                    for prov in proveedores_duenos:
                        print(f"     - ID: {prov.get('id')}, Proveedor: '{prov.get('proveedor_nombre')}', Dueño: {prov.get('dueno')}")
                
                # Verificar inconsistencias
                print("\n⚠️ Verificando inconsistencias...")
                if 'proveedores_inconsistentes' in consultas:
                    inconsistentes = consultas['proveedores_inconsistentes']
                    print(f"   Proveedores inconsistentes: {len(inconsistentes)}")
                    for prov in inconsistentes:
                        print(f"     - {prov}")
                
            except Exception as e:
                print(f"   Error parseando JSON: {e}")
                print(f"   Respuesta: {response.text[:500]}...")
        
        # Probar endpoint de búsqueda con diferentes parámetros
        print("\n🔍 Probando diferentes parámetros de búsqueda...")
        
        # 1. Búsqueda general
        print("   1. Búsqueda general...")
        url_busqueda = f"{base_url}/agregar_producto"
        params = {
            'busqueda_excel': 'CARBG7202',
            'solo_ricky': '1'
        }
        
        response = requests.get(url_busqueda, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("      ✅ Producto encontrado")
        else:
            print("      ❌ Producto NO encontrado")
        
        # 2. Búsqueda sin filtro de dueño
        print("   2. Búsqueda sin filtro de dueño...")
        params = {
            'busqueda_excel': 'CARBG7202'
        }
        
        response = requests.get(url_busqueda, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("      ✅ Producto encontrado")
        else:
            print("      ❌ Producto NO encontrado")
        
        # 3. Búsqueda por proveedor manual
        print("   3. Búsqueda por proveedor manual...")
        params = {
            'proveedor_excel_ricky': 'manual_9_ricky',
            'busqueda_excel': 'CARBG7202',
            'solo_ricky': '1'
        }
        
        response = requests.get(url_busqueda, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("      ✅ Producto encontrado")
        else:
            print("      ❌ Producto NO encontrado")
        
        # 4. Búsqueda por proveedor Excel
        print("   4. Búsqueda por proveedor Excel...")
        params = {
            'proveedor_excel_ricky': 'chiesa',
            'busqueda_excel': 'CARBG7202',
            'solo_ricky': '1'
        }
        
        response = requests.get(url_busqueda, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("      ✅ Producto encontrado")
        else:
            print("      ❌ Producto NO encontrado")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_producto_railway()


