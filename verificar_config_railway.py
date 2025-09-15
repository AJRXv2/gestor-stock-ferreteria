#!/usr/bin/env python3
"""
Script para verificar la configuración de base de datos en Railway
"""

import os

def verificar_config():
    """Verifica la configuración de base de datos"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    # Verificar variables de entorno
    print("📋 Variables de entorno:")
    print(f"   USE_POSTGRES: {os.environ.get('USE_POSTGRES', 'No definida')}")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'No definida')}")
    
    # Verificar si hay archivo .env
    if os.path.exists('.env'):
        print("\n📄 Archivo .env encontrado:")
        with open('.env', 'r') as f:
            for line in f:
                if 'DATABASE' in line or 'POSTGRES' in line:
                    print(f"   {line.strip()}")
    else:
        print("\n❌ No se encontró archivo .env")
    
    # Verificar railway.json
    if os.path.exists('railway.json'):
        print("\n📄 railway.json encontrado:")
        with open('railway.json', 'r') as f:
            content = f.read()
            print(f"   Contenido: {content[:200]}...")
    else:
        print("\n❌ No se encontró railway.json")
    
    # Verificar railway.toml
    if os.path.exists('railway.toml'):
        print("\n📄 railway.toml encontrado:")
        with open('railway.toml', 'r') as f:
            content = f.read()
            print(f"   Contenido: {content[:200]}...")
    else:
        print("\n❌ No se encontró railway.toml")

if __name__ == "__main__":
    verificar_config()
