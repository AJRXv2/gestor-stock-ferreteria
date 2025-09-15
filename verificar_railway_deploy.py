#!/usr/bin/env python3
"""
Script para verificar el deploy de Railway
"""

import requests
import json

def verificar_railway_deploy():
    """Verifica si Railway está funcionando correctamente"""
    
    print("🔍 VERIFICANDO DEPLOY DE RAILWAY")
    print("=" * 50)
    
    try:
        # URL de la aplicación en Railway
        url = "https://ferreteriacasapauluk.up.railway.app"
        
        print(f"📡 Probando conexión a: {url}")
        
        # Probar la página principal
        response = response = requests.get(url, timeout=10)
        print(f"✅ Página principal: {response.status_code}")
        
        # Probar la página de agregar producto
        url_agregar = f"{url}/agregar_producto"
        response = requests.get(url_agregar, timeout=10)
        print(f"✅ Página agregar producto: {response.status_code}")
        
        # Probar endpoint de diagnóstico si existe
        try:
            url_diagnostico = f"{url}/diagnostico_railway"
            response = requests.get(url_diagnostico, timeout=10)
            print(f"✅ Endpoint diagnóstico: {response.status_code}")
            if response.status_code == 200:
                print(f"   Respuesta: {response.text[:200]}...")
        except:
            print("⚠️ Endpoint diagnóstico no disponible")
        
        # Probar búsqueda específica
        try:
            url_busqueda = f"{url}/agregar_producto?proveedor_excel_ricky=manual_9_ricky&busqueda_excel=CARBG7202&solo_ricky=1"
            response = requests.get(url_busqueda, timeout=10)
            print(f"✅ Búsqueda específica: {response.status_code}")
            if "CARBG7202" in response.text:
                print("   ✅ Producto encontrado en la respuesta")
            else:
                print("   ❌ Producto NO encontrado en la respuesta")
        except Exception as e:
            print(f"❌ Error en búsqueda específica: {e}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    verificar_railway_deploy()
