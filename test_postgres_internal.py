#!/usr/bin/env python3
"""
Script para probar la conexión a PostgreSQL interno de Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def test_postgres_internal():
    """Prueba la conexión a PostgreSQL interno de Railway"""
    
    # URL interna de Railway
    DATABASE_URL_INTERNAL = "postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@postgres.railway.internal:5432/railway"
    
    print("🔍 PROBANDO CONEXIÓN A POSTGRESQL INTERNO DE RAILWAY")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos interna
        print("📡 Conectando a PostgreSQL interno...")
        conn = psycopg2.connect(DATABASE_URL_INTERNAL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Conexión interna exitosa!")
        
        # 1. Verificar productos_manual
        print("\n📦 1. PRODUCTOS EN productos_manual:")
        cursor.execute("SELECT id, nombre, codigo, precio, proveedor, dueno FROM productos_manual LIMIT 10")
        productos = cursor.fetchall()
        if productos:
            for prod in productos:
                print(f"   - ID: {prod['id']}, Código: {prod['codigo']}, Nombre: {prod['nombre'][:50]}..., Proveedor: {prod['proveedor']}, Dueño: {prod['dueno']}")
        else:
            print("   ❌ No hay productos en productos_manual")
        
        # 2. Buscar específicamente CARBG7202
        print("\n🔍 2. BÚSQUEDA ESPECÍFICA DE CARBG7202:")
        cursor.execute("SELECT * FROM productos_manual WHERE codigo ILIKE '%CARBG7202%'")
        producto_especifico = cursor.fetchall()
        if producto_especifico:
            for prod in producto_especifico:
                print(f"   ✅ ENCONTRADO: {dict(prod)}")
        else:
            print("   ❌ No se encontró CARBG7202 en productos_manual")
        
        # 3. Verificar proveedores_manual
        print("\n🏢 3. PROVEEDORES EN proveedores_manual:")
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre ILIKE '%chiesa%'")
        proveedores_manual = cursor.fetchall()
        if proveedores_manual:
            for prov in proveedores_manual:
                print(f"   - ID: {prov['id']}, Nombre: {prov['nombre']}, Dueño: {prov['dueno']}")
        else:
            print("   ❌ No se encontró Chiesa en proveedores_manual")
        
        # 4. Probar la consulta exacta que usa la función
        print("\n🧪 4. PRUEBA DE CONSULTA EXACTA:")
        if producto_especifico:
            for prod in producto_especifico:
                proveedor_nombre = prod['proveedor']
                dueno = prod['dueno']
                termino = 'CARBG7202'
                
                query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(%s) AND LOWER(dueno) = LOWER(%s) AND (LOWER(nombre) LIKE LOWER(%s) OR LOWER(codigo) LIKE LOWER(%s))"
                params = [proveedor_nombre, dueno, f"%{termino}%", f"%{termino}%"]
                
                print(f"   Consulta: {query}")
                print(f"   Parámetros: {params}")
                
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                print(f"   Resultados: {len(resultados)}")
                if resultados:
                    for r in resultados:
                        print(f"     - {dict(r)}")
        
        # 5. Contar total de productos por dueño
        print("\n📊 5. CONTEO DE PRODUCTOS POR DUEÑO:")
        cursor.execute("SELECT dueno, COUNT(*) as total FROM productos_manual GROUP BY dueno")
        conteos = cursor.fetchall()
        for conteo in conteos:
            print(f"   - {conteo['dueno']}: {conteo['total']} productos")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        print("\n✅ Diagnóstico interno completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico interno: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_postgres_internal()
