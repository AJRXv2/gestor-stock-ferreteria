#!/usr/bin/env python3
"""
Script de prueba para verificar que la separación de proveedores Excel/Manual funciona
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import db_query, PROVEEDOR_CONFIG
    
    print("🔍 Verificando separación de proveedores Excel/Manual...")
    
    # Verificar proveedores manuales en la base de datos
    print(f"\n1. Proveedores manuales en la base de datos:")
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
    
    # Verificar configuración de proveedores Excel
    print(f"\n3. Proveedores configurados para Excel:")
    for proveedor, config in PROVEEDOR_CONFIG.items():
        print(f"   - {proveedor}: {config.get('dueno')} (carpeta: {config.get('folder')})")
    
    # Verificar si hay conflictos (mismo nombre en Excel y Manual)
    print(f"\n4. Verificando conflictos de nombres:")
    if proveedores_manual and productos_manual:
        nombres_manual = {p['proveedor'].lower() for p in productos_manual}
        nombres_excel = {k.lower() for k in PROVEEDOR_CONFIG.keys()}
        
        conflictos = nombres_manual.intersection(nombres_excel)
        if conflictos:
            print(f"   ⚠️ Conflictos encontrados: {list(conflictos)}")
            print(f"   Estos proveedores aparecen tanto en Excel como en Manual")
        else:
            print(f"   ✅ No hay conflictos de nombres")
    
    # Simular construcción de dropdown
    print(f"\n5. Simulando construcción de dropdown:")
    
    # Proveedores Excel
    print(f"   Proveedores Excel de Ricky:")
    for key, config in PROVEEDOR_CONFIG.items():
        if config.get('dueno') == 'ricky':
            print(f"     - {key.title()} (Excel - Ricky)")
    
    print(f"   Proveedores Excel de Ferretería General:")
    for key, config in PROVEEDOR_CONFIG.items():
        if config.get('dueno') == 'ferreteria_general':
            print(f"     - {key.title()} (Excel - Ferretería General)")
    
    # Proveedores Manual
    if productos_manual:
        print(f"   Proveedores Manual:")
        for p in productos_manual:
            dueno_display = 'Ricky' if p['dueno'] == 'ricky' else 'Ferretería General'
            print(f"     - {p['proveedor']} (Manual - {dueno_display})")
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    print(traceback.format_exc())
