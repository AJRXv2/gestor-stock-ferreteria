#!/usr/bin/env python3
"""
Script para diagnosticar el problema exacto en Railway
"""

import os
import sys

# Configurar exactamente como Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@gondola.proxy.rlwy.net:10839/railway'
os.environ['USE_POSTGRES'] = '1'

def diagnostico_railway_exacto():
    """Diagnostica el problema exacto en Railway"""
    
    print("🔍 DIAGNÓSTICO EXACTO DE RAILWAY")
    print("=" * 50)
    
    try:
        from gestor import db_query, buscar_en_excel_manual_por_nombre_proveedor, buscar_en_excel_manual
        
        print("✅ Módulos importados correctamente")
        
        # 1. Verificar conexión directa
        print("\n📡 1. VERIFICANDO CONEXIÓN DIRECTA:")
        test_query = db_query("SELECT COUNT(*) as total FROM productos_manual", fetch=True)
        if test_query:
            print(f"   ✅ Total productos: {test_query[0]['total']}")
        else:
            print("   ❌ Error en conexión")
            return
        
        # 2. Verificar producto específico
        print("\n🔍 2. VERIFICANDO PRODUCTO ESPECÍFICO:")
        producto_query = db_query("SELECT * FROM productos_manual WHERE codigo = 'CARBG7202'", fetch=True)
        if producto_query:
            for prod in producto_query:
                print(f"   ✅ Producto encontrado: {dict(prod)}")
        else:
            print("   ❌ Producto no encontrado")
            return
        
        # 3. Probar función buscar_en_excel_manual_por_nombre_proveedor
        print("\n🔍 3. PROBANDO FUNCIÓN buscar_en_excel_manual_por_nombre_proveedor:")
        resultados = buscar_en_excel_manual_por_nombre_proveedor("CARBG7202", "Chiesa", "ricky")
        print(f"   Resultados: {len(resultados)}")
        for i, resultado in enumerate(resultados):
            print(f"     {i+1}. {resultado}")
        
        # 4. Probar función buscar_en_excel_manual
        print("\n🔍 4. PROBANDO FUNCIÓN buscar_en_excel_manual:")
        resultados_general = buscar_en_excel_manual("CARBG7202", "ricky")
        print(f"   Resultados: {len(resultados_general)}")
        for i, resultado in enumerate(resultados_general):
            print(f"     {i+1}. {resultado}")
        
        # 5. Probar consulta SQL exacta
        print("\n🔍 5. PROBANDO CONSULTA SQL EXACTA:")
        query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(?) AND LOWER(dueno) = LOWER(?) AND (LOWER(nombre) LIKE LOWER(?) OR LOWER(codigo) LIKE LOWER(?))"
        params = ['Chiesa', 'ricky', '%CARBG7202%', '%CARBG7202%']
        
        print(f"   Consulta: {query}")
        print(f"   Parámetros: {params}")
        
        resultados_sql = db_query(query, tuple(params), fetch=True)
        print(f"   Resultados SQL: {len(resultados_sql) if resultados_sql else 0}")
        if resultados_sql:
            for r in resultados_sql:
                print(f"     - {dict(r)}")
        
        # 6. Verificar si hay problema con la función db_query
        print("\n🔍 6. VERIFICANDO FUNCIÓN db_query:")
        try:
            # Probar consulta simple
            simple_query = db_query("SELECT codigo FROM productos_manual WHERE codigo = 'CARBG7202'", fetch=True)
            print(f"   Consulta simple: {len(simple_query) if simple_query else 0} resultados")
            if simple_query:
                print(f"     - {simple_query[0]}")
        except Exception as e:
            print(f"   ❌ Error en consulta simple: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    diagnostico_railway_exacto()
