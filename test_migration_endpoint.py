#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar el endpoint de migración localmente.
Este script simula una petición al endpoint /api/fix_railway_db.
"""

import os
import requests
import secrets
import sys

# Configuración
BASE_URL = "http://localhost:5000"  # Cambia si usas otro puerto
ENDPOINT = "/api/fix_railway_db"
TOKEN = os.environ.get('MIGRATION_TOKEN') or secrets.token_urlsafe(16)

def main():
    """Ejecutar la prueba del endpoint de migración"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(f"Uso: {sys.argv[0]} [token]")
        print("Si no se proporciona token, se usará MIGRATION_TOKEN del entorno o se generará uno aleatorio.")
        return
    
    # Usar token proporcionado o el valor por defecto
    token = sys.argv[1] if len(sys.argv) > 1 else TOKEN
    
    print(f"🔑 Token de migración: {token}")
    print(f"🌐 URL de prueba: {BASE_URL}{ENDPOINT}")
    print("⚠️ Asegúrate de que:")
    print("   1. El servidor Flask esté ejecutándose en localhost")
    print("   2. La variable MIGRATION_TOKEN esté configurada con el mismo valor en el servidor")
    
    try:
        # Enviar petición con el token en los headers
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
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

if __name__ == "__main__":
    main()