#!/usr/bin/env python3
"""
Script para probar búsqueda general en Railway
"""

import requests

def test_busqueda_general():
    """Prueba la búsqueda general en Railway"""
    
    print("🔍 PROBANDO BÚSQUEDA GENERAL EN RAILWAY")
    print("=" * 50)
    
    try:
        base_url = "https://ferreteriacasapauluk.up.railway.app"
        
        # Probar búsqueda general (Todos los proveedores)
        print("🔍 Probando búsqueda general (Todos los proveedores)...")
        url_general = f"{base_url}/agregar_producto?busqueda_excel=CARBG7202&solo_ricky=1"
        response = requests.get(url_general, timeout=10)
        print(f"✅ Búsqueda general: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("   ✅ Producto encontrado en búsqueda general")
        else:
            print("   ❌ Producto NO encontrado en búsqueda general")
        
        # Probar búsqueda específica por proveedor manual
        print("\n🔍 Probando búsqueda específica por proveedor manual...")
        url_manual = f"{base_url}/agregar_producto?proveedor_excel_ricky=manual_9_ricky&busqueda_excel=CARBG7202&solo_ricky=1"
        response = requests.get(url_manual, timeout=10)
        print(f"✅ Búsqueda manual: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("   ✅ Producto encontrado en búsqueda manual")
        else:
            print("   ❌ Producto NO encontrado en búsqueda manual")
        
        # Probar búsqueda por proveedor Excel
        print("\n🔍 Probando búsqueda por proveedor Excel...")
        url_excel = f"{base_url}/agregar_producto?proveedor_excel_ricky=chiesa&busqueda_excel=CARBG7202&solo_ricky=1"
        response = requests.get(url_excel, timeout=10)
        print(f"✅ Búsqueda Excel: {response.status_code}")
        
        if "CARBG7202" in response.text:
            print("   ✅ Producto encontrado en búsqueda Excel")
        else:
            print("   ❌ Producto NO encontrado en búsqueda Excel")
        
        # Verificar el contenido de la respuesta
        print("\n📄 Contenido de la respuesta (primeros 500 caracteres):")
        print(response.text[:500])
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_busqueda_general()

