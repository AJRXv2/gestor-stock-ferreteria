"""
Script para ejecutar el endpoint de limpieza de la base de datos Railway.
"""

import requests
import json
import os
import sys

# URL por defecto (cambiar según corresponda)
DEFAULT_URL = "http://localhost:5000/api/clean_railway_db"

def execute_clean_endpoint(url=None, token=None):
    """Ejecuta el endpoint de limpieza de la base de datos.
    
    Args:
        url (str, optional): URL del endpoint. Si no se proporciona, se usa el valor por defecto.
        token (str, optional): Token de migración. Si no se proporciona, se intenta obtener de la variable de entorno.
    
    Returns:
        dict: Resultado de la ejecución
    """
    target_url = url or os.environ.get('APP_URL', DEFAULT_URL)
    migration_token = token or os.environ.get('MIGRATION_TOKEN', 'default_migration_token')
    
    print(f"Ejecutando limpieza en: {target_url}")
    
    headers = {
        'X-Migration-Token': migration_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(target_url, headers=headers, timeout=30)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        result = response.json()
        
        if result.get('success'):
            print("✅ Limpieza ejecutada correctamente")
            print(f"Mensaje: {result.get('mensaje', '')}")
            
            # Mostrar detalles de tablas limpiadas
            if 'tablas_limpiadas' in result:
                print("\nTablas limpiadas:")
                for tabla in result['tablas_limpiadas']:
                    print(f"- {tabla}")
            
            # Mostrar detalles de registros eliminados
            if 'registros_eliminados' in result:
                print("\nRegistros eliminados:")
                for tabla, info in result['registros_eliminados'].items():
                    print(f"- {tabla}: {info.get('deleted', 0)} registros")
            
            return result
        else:
            print(f"❌ Error: {result.get('mensaje', 'Error desconocido')}")
            if 'error' in result:
                print(f"Detalles: {result['error']}")
            return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return {
            "success": False,
            "mensaje": f"Error de conexión: {str(e)}"
        }
    except json.JSONDecodeError:
        print("❌ Error: La respuesta no es un JSON válido")
        return {
            "success": False,
            "mensaje": "La respuesta no es un JSON válido"
        }
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return {
            "success": False,
            "mensaje": f"Error inesperado: {str(e)}"
        }

if __name__ == "__main__":
    # Procesar argumentos de línea de comandos
    import argparse
    parser = argparse.ArgumentParser(description='Ejecutar el endpoint de limpieza de la base de datos Railway.')
    parser.add_argument('--url', help='URL del endpoint')
    parser.add_argument('--token', help='Token de migración')
    
    args = parser.parse_args()
    
    # Ejecutar el endpoint
    result = execute_clean_endpoint(args.url, args.token)
    
    # Salir con código de error si hay problemas
    if not result.get('success'):
        sys.exit(1)