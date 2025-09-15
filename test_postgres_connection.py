#!/usr/bin/env python3
"""
Script para probar la conexión directa a PostgreSQL de Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def test_postgres_connection():
    """Prueba la conexión directa a PostgreSQL de Railway"""
    
    # URL de conexión de Railway
    DATABASE_URL = "postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@gondola.proxy.rlwy.net:10839/railway"
    
    print("🔍 PROBANDO CONEXIÓN A POSTGRESQL DE RAILWAY")
    print("=" * 50)
    
    try:
        # Conectar a la base de datos
        print("📡 Conectando a PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Conexión exitosa!")
        
        # 1. Verificar tablas existentes
        print("\n📋 1. TABLAS EXISTENTES:")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tablas = cursor.fetchall()
        for tabla in tablas:
            print(f"   - {tabla['table_name']}")
        
        # 2. Verificar productos_manual
        print("\n📦 2. PRODUCTOS EN productos_manual:")
        cursor.execute("SELECT id, nombre, codigo, precio, proveedor, dueno FROM productos_manual LIMIT 10")
        productos = cursor.fetchall()
        if productos:
            for prod in productos:
                print(f"   - ID: {prod['id']}, Código: {prod['codigo']}, Nombre: {prod['nombre'][:50]}..., Proveedor: {prod['proveedor']}, Dueño: {prod['dueno']}")
        else:
            print("   ❌ No hay productos en productos_manual")
        
        # 3. Buscar específicamente CARBG7202
        print("\n🔍 3. BÚSQUEDA ESPECÍFICA DE CARBG7202:")
        cursor.execute("SELECT * FROM productos_manual WHERE codigo ILIKE '%CARBG7202%'")
        producto_especifico = cursor.fetchall()
        if producto_especifico:
            for prod in producto_especifico:
                print(f"   ✅ ENCONTRADO: {dict(prod)}")
        else:
            print("   ❌ No se encontró CARBG7202 en productos_manual")
        
        # 4. Verificar proveedores_manual
        print("\n🏢 4. PROVEEDORES EN proveedores_manual:")
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre ILIKE '%chiesa%'")
        proveedores_manual = cursor.fetchall()
        if proveedores_manual:
            for prov in proveedores_manual:
                print(f"   - ID: {prov['id']}, Nombre: {prov['nombre']}, Dueño: {prov['dueno']}")
        else:
            print("   ❌ No se encontró Chiesa en proveedores_manual")
        
        # 5. Verificar proveedores_meta
        print("\n🏢 5. PROVEEDORES EN proveedores_meta:")
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_meta WHERE nombre ILIKE '%chiesa%'")
        proveedores_meta = cursor.fetchall()
        if proveedores_meta:
            for prov in proveedores_meta:
                print(f"   - ID: {prov['id']}, Nombre: {prov['nombre']}, Dueño: {prov['dueno']}")
        else:
            print("   ❌ No se encontró Chiesa en proveedores_meta")
        
        # 6. Verificar relación entre productos y proveedores
        print("\n🔗 6. RELACIÓN PRODUCTOS-PROVEEDORES:")
        if producto_especifico:
            for prod in producto_especifico:
                proveedor_nombre = prod['proveedor']
                print(f"   Producto {prod['codigo']} tiene proveedor: '{proveedor_nombre}'")
                
                # Buscar en proveedores_manual
                cursor.execute("SELECT id, nombre FROM proveedores_manual WHERE nombre ILIKE %s", (f"%{proveedor_nombre}%",))
                prov_manual = cursor.fetchall()
                if prov_manual:
                    print(f"     ✅ Encontrado en proveedores_manual: {[dict(p) for p in prov_manual]}")
                else:
                    print(f"     ❌ NO encontrado en proveedores_manual")
                
                # Buscar en proveedores_meta
                cursor.execute("SELECT id, nombre FROM proveedores_meta WHERE nombre ILIKE %s", (f"%{proveedor_nombre}%",))
                prov_meta = cursor.fetchall()
                if prov_meta:
                    print(f"     ✅ Encontrado en proveedores_meta: {[dict(p) for p in prov_meta]}")
                else:
                    print(f"     ❌ NO encontrado en proveedores_meta")
        
        # 7. Probar la consulta exacta que usa la función
        print("\n🧪 7. PRUEBA DE CONSULTA EXACTA:")
        if producto_especifico:
            for prod in producto_especifico:
                proveedor_nombre = prod['proveedor']
                dueno = prod['dueno']
                termino = 'CARBG7202'
                
                query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(%s)"
                params = [proveedor_nombre]
                
                if dueno:
                    query += " AND LOWER(dueno) = LOWER(%s)"
                    params.append(dueno)
                
                if termino:
                    query += " AND (LOWER(nombre) LIKE LOWER(%s) OR LOWER(codigo) LIKE LOWER(%s))"
                    params.extend([f"%{termino}%", f"%{termino}%"])
                
                print(f"   Consulta: {query}")
                print(f"   Parámetros: {params}")
                
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                print(f"   Resultados: {len(resultados)}")
                if resultados:
                    for r in resultados:
                        print(f"     - {dict(r)}")
        
        # 8. Contar total de productos por dueño
        print("\n📊 8. CONTEO DE PRODUCTOS POR DUEÑO:")
        cursor.execute("SELECT dueno, COUNT(*) as total FROM productos_manual GROUP BY dueno")
        conteos = cursor.fetchall()
        for conteo in conteos:
            print(f"   - {conteo['dueno']}: {conteo['total']} productos")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        print("\n✅ Diagnóstico completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_postgres_connection()
