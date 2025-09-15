#!/usr/bin/env python3
"""
Script para diagnosticar el problema del filtro por Chiesa
"""

import os
import sys

# Configurar para usar PostgreSQL (Railway)
os.environ['DATABASE_URL'] = 'postgresql://postgres:GHGgzCejqiTgWHIHOhQSNLUYMVRgSjVl@gondola.proxy.rlwy.net:10839/railway'
os.environ['USE_POSTGRES'] = '1'

def diagnosticar_filtro_chiesa():
    """Diagnostica el problema del filtro por Chiesa"""
    
    print("🔍 DIAGNÓSTICO DEL FILTRO POR CHIESA")
    print("=" * 50)
    
    try:
        from gestor import db_query, buscar_en_excel
        
        print("✅ Módulos importados correctamente")
        
        # 1. Verificar qué proveedores están disponibles
        print("\n📋 1. PROVEEDORES DISPONIBLES:")
        proveedores = db_query("SELECT id, nombre, dueno FROM proveedores_manual WHERE nombre ILIKE '%chiesa%'", fetch=True)
        if proveedores:
            for prov in proveedores:
                print(f"   - ID: {prov['id']}, Nombre: '{prov['nombre']}', Dueño: {prov['dueno']}")
        else:
            print("   ❌ No se encontró Chiesa en proveedores_manual")
        
        # 2. Verificar productos de Chiesa
        print("\n📦 2. PRODUCTOS DE CHIESA:")
        productos_chiesa = db_query("SELECT id, nombre, codigo, proveedor, dueno FROM productos_manual WHERE proveedor ILIKE '%chiesa%'", fetch=True)
        if productos_chiesa:
            for prod in productos_chiesa:
                print(f"   - ID: {prod['id']}, Código: '{prod['codigo']}', Nombre: '{prod['nombre']}', Proveedor: '{prod['proveedor']}', Dueño: {prod['dueno']}")
        else:
            print("   ❌ No se encontraron productos de Chiesa")
        
        # 3. Probar búsqueda "Todos (Ricky)" - debería funcionar
        print("\n🔍 3. BÚSQUEDA 'TODOS (RICKY)' (debería funcionar):")
        resultados_todos = buscar_en_excel("CARBG7202", None, None, solo_ricky=True, solo_fg=False)
        print(f"   Resultados: {len(resultados_todos)}")
        for i, resultado in enumerate(resultados_todos):
            print(f"     {i+1}. {resultado}")
        
        # 4. Probar búsqueda específica por Chiesa (Manual) - ID 9
        print("\n🔍 4. BÚSQUEDA 'CHIESA (MANUAL - RICKY)' (ID 9):")
        resultados_manual = buscar_en_excel("CARBG7202", "manual_9_ricky", None, solo_ricky=True, solo_fg=False)
        print(f"   Resultados: {len(resultados_manual)}")
        for i, resultado in enumerate(resultados_manual):
            print(f"     {i+1}. {resultado}")
        
        # 5. Probar búsqueda por Chiesa (Excel)
        print("\n🔍 5. BÚSQUEDA 'CHIESA (EXCEL - RICKY)':")
        resultados_excel = buscar_en_excel("CARBG7202", "chiesa", None, solo_ricky=True, solo_fg=False)
        print(f"   Resultados: {len(resultados_excel)}")
        for i, resultado in enumerate(resultados_excel):
            print(f"     {i+1}. {resultado}")
        
        # 6. Verificar la lógica de filtrado en la función buscar_en_excel
        print("\n🔍 6. ANÁLISIS DE LA LÓGICA DE FILTRADO:")
        
        # Simular el filtro que se aplica en la función
        proveedor_filtro = "manual_9_ricky"
        print(f"   Proveedor filtro: '{proveedor_filtro}'")
        print(f"   ¿Empieza con 'manual_'? {proveedor_filtro.startswith('manual_')}")
        
        if proveedor_filtro.startswith('manual_'):
            try:
                _, rest = proveedor_filtro.split('manual_', 1)
                parts = rest.split('_', 1)
                proveedor_id = int(parts[0])
                dueno_sel = parts[1] if len(parts) > 1 else None
                print(f"   Proveedor ID extraído: {proveedor_id}")
                print(f"   Dueño extraído: {dueno_sel}")
                
                # Verificar si el proveedor existe
                prov_data = db_query("SELECT nombre FROM proveedores_manual WHERE id = ?", (proveedor_id,), fetch=True)
                if prov_data:
                    nombre_proveedor = prov_data[0]['nombre']
                    print(f"   Nombre del proveedor: '{nombre_proveedor}'")
                    
                    # Probar la consulta exacta
                    query = "SELECT id, nombre, codigo, precio, proveedor, observaciones, dueno FROM productos_manual WHERE LOWER(proveedor) = LOWER(?)"
                    params = [nombre_proveedor]
                    
                    if dueno_sel:
                        query += " AND LOWER(dueno) = LOWER(?)"
                        params.append(dueno_sel)
                    
                    query += " AND (LOWER(nombre) LIKE LOWER(?) OR LOWER(codigo) LIKE LOWER(?))"
                    params.extend([f"%CARBG7202%", f"%CARBG7202%"])
                    
                    print(f"   Consulta final: {query}")
                    print(f"   Parámetros: {params}")
                    
                    resultados = db_query(query, tuple(params), fetch=True)
                    print(f"   Resultados de la consulta: {len(resultados) if resultados else 0}")
                    if resultados:
                        for r in resultados:
                            print(f"     - {dict(r)}")
                else:
                    print(f"   ❌ Proveedor con ID {proveedor_id} no encontrado")
                    
            except (ValueError, TypeError) as e:
                print(f"   ❌ Error al procesar filtro: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    diagnosticar_filtro_chiesa()

