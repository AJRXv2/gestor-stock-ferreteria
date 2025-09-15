#!/usr/bin/env python3
"""
Script para probar la aplicación con la configuración de Railway
"""

import os
import sys

# Configurar variables de entorno como Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@gondola.proxy.rlwy.net:10839/railway'
os.environ['USE_POSTGRES'] = '1'

def test_with_railway_config():
    """Prueba la aplicación con la configuración de Railway"""
    
    print("🔍 PROBANDO CON CONFIGURACIÓN DE RAILWAY")
    print("=" * 50)
    
    try:
        # Importar después de configurar las variables de entorno
        from gestor import db_query, buscar_en_excel_manual_por_nombre_proveedor, buscar_en_excel_manual
        
        print("✅ Módulos importados correctamente")
        
        # Probar conexión a base de datos
        print("\n📡 Probando conexión a base de datos...")
        test_query = db_query("SELECT COUNT(*) as total FROM productos_manual", fetch=True)
        if test_query:
            print(f"✅ Conexión exitosa. Total productos: {test_query[0]['total']}")
        else:
            print("❌ Error en la conexión")
            return
        
        # Probar búsqueda específica
        print("\n🔍 Probando búsqueda específica de CARBG7202 en Chiesa...")
        resultados = buscar_en_excel_manual_por_nombre_proveedor("CARBG7202", "Chiesa", "ricky")
        print(f"📊 Resultados encontrados: {len(resultados)}")
        for i, resultado in enumerate(resultados):
            print(f"   {i+1}. {resultado}")
        
        # Probar búsqueda general
        print("\n🔍 Probando búsqueda general de CARBG7202...")
        resultados_general = buscar_en_excel_manual("CARBG7202", "ricky")
        print(f"📊 Resultados generales encontrados: {len(resultados_general)}")
        for i, resultado in enumerate(resultados_general):
            print(f"   {i+1}. {resultado}")
        
        # Probar búsqueda sin filtro de dueño
        print("\n🔍 Probando búsqueda sin filtro de dueño...")
        resultados_sin_dueno = buscar_en_excel_manual("CARBG7202", None)
        print(f"📊 Resultados sin dueño: {len(resultados_sin_dueno)}")
        for i, resultado in enumerate(resultados_sin_dueno):
            print(f"   {i+1}. {resultado}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_with_railway_config()

