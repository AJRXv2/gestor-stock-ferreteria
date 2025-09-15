#!/usr/bin/env python3
"""
Script para diagnosticar la base de datos PostgreSQL en Railway
"""

import os
import sys

# Configurar para usar PostgreSQL (Railway)
os.environ['USE_POSTGRES'] = '1'
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/railway'  # Placeholder

def diagnosticar_bd():
    """Diagnostica la base de datos PostgreSQL"""
    
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS POSTGRESQL")
    print("=" * 50)
    
    try:
        # Importar después de configurar las variables de entorno
        from gestor import db_query
        
        print("✅ Conexión a base de datos establecida")
        
        # 1. Verificar tablas existentes
        print("\n📋 1. TABLAS EXISTENTES:")
        tablas = db_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", fetch=True)
        for tabla in tablas:
            print(f"   - {tabla['table_name']}")
        
        # 2. Verificar productos_manual
        print("\n📦 2. PRODUCTOS EN productos_manual:")
        productos = db_query("SELECT id, nombre, codigo, precio, proveedor, dueno FROM productos_manual LIMIT 10", fetch=True)
        if productos:
            for prod in productos:
                print(f"   - ID: {prod['id']}, Código: {prod['codigo']}, Nombre: {prod['nombre'][:50]}..., Proveedor: {prod['proveedor']}, Dueño: {prod['dueno']}")
        else:
            print("   ❌ No hay productos en productos_manual")
        
        # 3. Buscar específicamente CARBG7202
        print("\n🔍 3. BÚSQUEDA ESPECÍFICA DE CARBG7202:")
        producto_especifico = db_query("SELECT * FROM productos_manual WHERE codigo ILIKE '%CARBG7202%'", fetch=True)
        if producto_especifico:
            for prod in producto_especifico:
                print(f"   ✅ ENCONTRADO: {prod}")
        else:
            print("   ❌ No se encontró CARBG7202 en productos_manual")
        
        # 4. Verificar proveedores_manual
        print("\n🏢 4. PROVEEDORES EN proveedores_manual:")
        proveedores_manual = db_query("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre ILIKE '%chiesa%'", fetch=True)
        if proveedores_manual:
            for prov in proveedores_manual:
                print(f"   - ID: {prov['id']}, Nombre: {prov['nombre']}, Dueño: {prov['dueno']}")
        else:
            print("   ❌ No se encontró Chiesa en proveedores_manual")
        
        # 5. Verificar proveedores_meta
        print("\n🏢 5. PROVEEDORES EN proveedores_meta:")
        proveedores_meta = db_query("SELECT id, nombre, dueno FROM proveedores_meta WHERE nombre ILIKE '%chiesa%'", fetch=True)
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
                prov_manual = db_query("SELECT id, nombre FROM proveedores_manual WHERE nombre ILIKE ?", (f"%{proveedor_nombre}%",), fetch=True)
                if prov_manual:
                    print(f"     ✅ Encontrado en proveedores_manual: {prov_manual}")
                else:
                    print(f"     ❌ NO encontrado en proveedores_manual")
                
                # Buscar en proveedores_meta
                prov_meta = db_query("SELECT id, nombre FROM proveedores_meta WHERE nombre ILIKE ?", (f"%{proveedor_nombre}%",), fetch=True)
                if prov_meta:
                    print(f"     ✅ Encontrado en proveedores_meta: {prov_meta}")
                else:
                    print(f"     ❌ NO encontrado en proveedores_meta")
        
        # 7. Probar la consulta exacta que usa la función
        print("\n🧪 7. PRUEBA DE CONSULTA EXACTA:")
        if producto_especifico:
            for prod in producto_especifico:
                proveedor_nombre = prod['proveedor']
                dueno = prod['dueno']
                termino = 'CARBG7202'
                
                query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(?)"
                params = [proveedor_nombre]
                
                if dueno:
                    query += " AND LOWER(dueno) = LOWER(?)"
                    params.append(dueno)
                
                if termino:
                    query += " AND (LOWER(nombre) LIKE LOWER(?) OR LOWER(codigo) LIKE LOWER(?))"
                    params.extend([f"%{termino}%", f"%{termino}%"])
                
                print(f"   Consulta: {query}")
                print(f"   Parámetros: {params}")
                
                resultados = db_query(query, tuple(params), fetch=True)
                print(f"   Resultados: {len(resultados) if resultados else 0}")
                if resultados:
                    for r in resultados:
                        print(f"     - {r}")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    diagnosticar_bd()
