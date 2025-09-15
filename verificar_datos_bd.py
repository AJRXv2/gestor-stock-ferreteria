#!/usr/bin/env python3
"""
Script para verificar qué datos hay en la base de datos
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import db_query
    
    print("🔍 Verificando datos en la base de datos...")
    
    # Verificar productos_manual
    print("\n1. Productos en tabla productos_manual:")
    productos = db_query("SELECT codigo, nombre, proveedor, dueno FROM productos_manual LIMIT 10", fetch=True)
    if productos:
        print(f"   Total productos: {len(productos)}")
        for p in productos:
            print(f"   - {p.get('codigo')}: {p.get('nombre')} ({p.get('proveedor')}) - Dueño: {p.get('dueno')}")
    else:
        print("   No hay productos en productos_manual")
    
    # Verificar proveedores únicos
    print("\n2. Proveedores únicos en productos_manual:")
    proveedores = db_query("SELECT DISTINCT proveedor FROM productos_manual ORDER BY proveedor", fetch=True)
    if proveedores:
        for p in proveedores:
            print(f"   - {p.get('proveedor')}")
    else:
        print("   No hay proveedores")
    
    # Verificar códigos que contengan "CARBG"
    print("\n3. Códigos que contengan 'CARBG':")
    codigos = db_query("SELECT codigo, nombre, proveedor FROM productos_manual WHERE codigo LIKE '%CARBG%'", fetch=True)
    if codigos:
        for c in codigos:
            print(f"   - {c.get('codigo')}: {c.get('nombre')} ({c.get('proveedor')})")
    else:
        print("   No se encontraron códigos con 'CARBG'")
    
    # Verificar si existe el código exacto
    print("\n4. Búsqueda del código exacto 'CARBG7202':")
    exacto = db_query("SELECT * FROM productos_manual WHERE codigo = 'CARBG7202'", fetch=True)
    if exacto:
        for e in exacto:
            print(f"   - {e.get('codigo')}: {e.get('nombre')} ({e.get('proveedor')}) - Dueño: {e.get('dueno')}")
    else:
        print("   No se encontró el código exacto 'CARBG7202'")
    
    # Verificar proveedor "chiesa"
    print("\n5. Productos del proveedor 'chiesa':")
    chiesa = db_query("SELECT codigo, nombre FROM productos_manual WHERE LOWER(proveedor) = LOWER('chiesa')", fetch=True)
    if chiesa:
        for c in chiesa:
            print(f"   - {c.get('codigo')}: {c.get('nombre')}")
    else:
        print("   No se encontraron productos del proveedor 'chiesa'")
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    print(traceback.format_exc())
