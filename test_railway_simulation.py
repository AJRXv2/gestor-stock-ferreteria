#!/usr/bin/env python3
"""
Script para simular exactamente lo que Railway debería estar haciendo
"""

import os
import sys

# Simular la configuración de Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@gondola.proxy.rlwy.net:10839/railway'
os.environ['USE_POSTGRES'] = '1'

def test_railway_simulation():
    """Simula exactamente lo que Railway debería estar haciendo"""
    
    print("🔍 SIMULANDO CONFIGURACIÓN DE RAILWAY")
    print("=" * 50)
    
    try:
        # Importar después de configurar las variables de entorno
        from gestor import db_query, buscar_en_excel, _is_postgres_configured
        
        print("✅ Módulos importados correctamente")
        
        # Verificar configuración de PostgreSQL
        print(f"\n📋 Configuración PostgreSQL:")
        print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'No definida')}")
        print(f"   USE_POSTGRES: {os.environ.get('USE_POSTGRES', 'No definida')}")
        print(f"   _is_postgres_configured(): {_is_postgres_configured()}")
        
        # Probar conexión a base de datos
        print("\n📡 Probando conexión a base de datos...")
        test_query = db_query("SELECT COUNT(*) as total FROM productos_manual", fetch=True)
        if test_query:
            print(f"✅ Conexión exitosa. Total productos: {test_query[0]['total']}")
        else:
            print("❌ Error en la conexión")
            return
        
        # Probar la función buscar_en_excel completa
        print("\n🔍 Probando función buscar_en_excel completa...")
        
        # Simular búsqueda "Todos (Ricky)"
        print("   - Búsqueda 'Todos (Ricky)'...")
        resultados_todos = buscar_en_excel("CARBG7202", None, None, solo_ricky=True, solo_fg=False)
        print(f"     Resultados: {len(resultados_todos)}")
        for i, resultado in enumerate(resultados_todos):
            print(f"       {i+1}. {resultado}")
        
        # Simular búsqueda específica "Chiesa (Manual - Ricky)"
        print("   - Búsqueda 'Chiesa (Manual - Ricky)'...")
        resultados_chiesa = buscar_en_excel("CARBG7202", "manual_9_ricky", None, solo_ricky=True, solo_fg=False)
        print(f"     Resultados: {len(resultados_chiesa)}")
        for i, resultado in enumerate(resultados_chiesa):
            print(f"       {i+1}. {resultado}")
        
        # Simular búsqueda por proveedor Excel "Chiesa (Excel - Ricky)"
        print("   - Búsqueda 'Chiesa (Excel - Ricky)'...")
        resultados_excel = buscar_en_excel("CARBG7202", "chiesa", None, solo_ricky=True, solo_fg=False)
        print(f"     Resultados: {len(resultados_excel)}")
        for i, resultado in enumerate(resultados_excel):
            print(f"       {i+1}. {resultado}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_railway_simulation()


