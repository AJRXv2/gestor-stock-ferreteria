#!/usr/bin/env python3
"""
Script de prueba para verificar que la búsqueda por proveedor manual específico funciona
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import db_query, buscar_en_excel_manual_por_proveedor
    
    print("🔍 Verificando búsqueda por proveedor manual específico...")
    
    # Verificar proveedores manuales disponibles
    print(f"\n1. Proveedores manuales disponibles:")
    proveedores_manual = db_query("SELECT id, nombre FROM proveedores_manual ORDER BY nombre", fetch=True)
    if proveedores_manual:
        for p in proveedores_manual:
            print(f"   - ID {p['id']}: {p['nombre']}")
    else:
        print("   No hay proveedores manuales")
    
    # Verificar productos de proveedores manuales
    print(f"\n2. Productos de proveedores manuales:")
    productos_manual = db_query("SELECT DISTINCT proveedor, dueno FROM productos_manual ORDER BY proveedor", fetch=True)
    if productos_manual:
        for p in productos_manual:
            print(f"   - {p['proveedor']} ({p['dueno']})")
    else:
        print("   No hay productos manuales")
    
    # Buscar Chiesa específicamente
    print(f"\n3. Buscando Chiesa (ID 2300) específicamente:")
    chiesa_id = 2300
    termino_busqueda = "CARBG7202"  # El código que mencionaste
    
    try:
        resultados = buscar_en_excel_manual_por_proveedor(termino_busqueda, chiesa_id, "ricky")
        print(f"   Resultados encontrados: {len(resultados)}")
        for r in resultados:
            print(f"     - {r.get('codigo', 'N/A')} - {r.get('nombre', 'N/A')} - ${r.get('precio', 0)}")
    except Exception as e:
        print(f"   ❌ Error en búsqueda específica: {e}")
        import traceback
        print(traceback.format_exc())
    
    # Buscar sin filtro de proveedor (todos)
    print(f"\n4. Buscando en todos los proveedores manuales:")
    try:
        from gestor import buscar_en_excel_manual
        resultados_todos = buscar_en_excel_manual(termino_busqueda, "ricky")
        print(f"   Resultados encontrados: {len(resultados_todos)}")
        for r in resultados_todos:
            print(f"     - {r.get('codigo', 'N/A')} - {r.get('nombre', 'N/A')} - ${r.get('precio', 0)} - {r.get('proveedor', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error en búsqueda general: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    print(traceback.format_exc())
