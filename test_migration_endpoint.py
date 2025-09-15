#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar endpoints de migración y corrección en Railway.
Este script simula peticiones a los endpoints de mantenimiento.
"""

import os
import requests
import secrets
import sys

# Configuración
BASE_URL = "http://localhost:5000"  # Cambia si usas otro puerto
ENDPOINTS = {
    "fix_db": "/api/fix_railway_db",
    "fix_proveedores_case": "/api/fix_railway_proveedores_case",
    "diagnostico_railway": "/diagnostico_railway",
    "diagnostico_busqueda": "/diagnostico_busqueda"
}
TOKEN = os.environ.get('MIGRATION_TOKEN') or secrets.token_urlsafe(16)

def main():
    """Ejecutar la prueba de endpoints de Railway"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(f"Uso: {sys.argv[0]} [endpoint] [token]")
        print("Endpoints disponibles:")
        for key, url in ENDPOINTS.items():
            print(f"  - {key} ({url})")
        print("\nSi no se proporciona endpoint, se usará 'fix_db'.")
        print("Si no se proporciona token, se usará MIGRATION_TOKEN del entorno o se generará uno aleatorio.")
        return
    
    # Usar endpoint proporcionado o el valor por defecto
    endpoint_key = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ENDPOINTS else "fix_db"
    endpoint = ENDPOINTS[endpoint_key]
    
    # Usar token proporcionado o el valor por defecto
    token_arg_index = 2 if len(sys.argv) > 1 and sys.argv[1] in ENDPOINTS else 1
    token = sys.argv[token_arg_index] if len(sys.argv) > token_arg_index else TOKEN
    
    print(f"� Endpoint seleccionado: {endpoint_key} ({endpoint})")
    print(f"�🔑 Token de migración: {token}")
    print(f"🌐 URL completa: {BASE_URL}{endpoint}")
    print("⚠️ Asegúrate de que:")
    print("   1. El servidor Flask esté ejecutándose en localhost")
    
    if endpoint_key in ["fix_db", "fix_proveedores_case"]:
        print("   2. La variable MIGRATION_TOKEN esté configurada con el mismo valor en el servidor")
        try:
            # Enviar petición con el token en los headers
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                headers={"X-Migration-Token": token}
            )
            
            # Mostrar resultado
            print("\n📡 Respuesta del servidor:")
            print(f"   Código: {response.status_code}")
            try:
                json_data = response.json()
                print(f"   Éxito: {'✅' if json_data.get('success') else '❌'}")
                print(f"   Mensaje: {json_data.get('message')}")
            except:
                print(f"   Contenido: {response.text[:100]}...")
        except Exception as e:
            print(f"\n❌ Error al realizar la petición: {e}")
            print("   Verifica que el servidor esté en ejecución.")
    else:
        # Endpoints de diagnóstico
        try:
            # Para diagnóstico_busqueda, agregar parámetros de prueba
            params = {}
            if endpoint_key == "diagnostico_busqueda":
                params = {
                    "proveedor": "jeluz",
                    "termino": "cable"
                }
                print(f"📊 Parámetros de diagnóstico: {params}")
            
            # Enviar petición GET
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
            
            # Mostrar resultado
            print("\n📡 Respuesta del servidor:")
            print(f"   Código: {response.status_code}")
            try:
                json_data = response.json()
                if 'error' in json_data:
                    print(f"   Error: {'❌' if json_data.get('error') else '✅'}")
                print(f"   Ambiente: {json_data.get('ambiente')}")
                
                # Mostrar resumen de resultados según el endpoint
                if endpoint_key == "diagnostico_railway":
                    print(f"   Tablas encontradas: {len(json_data.get('tablas', {}).get('lista', []))}")
                    errores = json_data.get('errores', [])
                    if errores:
                        print(f"   Errores encontrados: {len(errores)}")
                        for err in errores[:3]:
                            print(f"     - {err}")
                elif endpoint_key == "diagnostico_busqueda":
                    pruebas = json_data.get('pruebas', {})
                    for k, v in pruebas.items():
                        if isinstance(v, dict) and 'resultados' in v:
                            print(f"   Prueba '{k}': {v.get('resultados')} resultados")
                
                print(f"\n💾 Respuesta JSON guardada en 'diagnostico_{endpoint_key}.json'")
                with open(f"diagnostico_{endpoint_key}.json", "w", encoding="utf-8") as f:
                    import json
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                print(f"   Error al procesar respuesta JSON: {e}")
                print(f"   Contenido: {response.text[:100]}...")
        except Exception as e:
            print(f"\n❌ Error al realizar la petición: {e}")
            print("   Verifica que el servidor esté en ejecución.")

if __name__ == "__main__":
    main()