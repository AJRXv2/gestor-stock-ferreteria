#!/usr/bin/env python3
"""
Script de prueba para verificar que la búsqueda en base de datos funciona correctamente
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import buscar_en_excel, db_query
    
    print("🔍 Probando búsqueda en base de datos...")
    
    # Probar búsqueda básica
    print("\n1. Búsqueda básica sin filtros:")
    resultados = buscar_en_excel("CARBG7202")
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:  # Mostrar solo los primeros 3
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')})")
    
    # Probar búsqueda con proveedor específico
    print("\n2. Búsqueda con proveedor 'chiesa':")
    resultados = buscar_en_excel("CARBG7202", proveedor_filtro="chiesa")
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')})")
    
    # Probar búsqueda solo para Ricky
    print("\n3. Búsqueda solo para Ricky:")
    resultados = buscar_en_excel("CARBG7202", solo_ricky=True)
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')}) - Dueño: {r.get('dueno')}")
    
    # Verificar conexión a la base de datos
    print("\n4. Verificando conexión a la base de datos:")
    try:
        productos = db_query("SELECT COUNT(*) as total FROM productos_manual", fetch=True)
        if productos:
            print(f"   ✅ Conexión exitosa. Total productos en BD: {productos[0]['total']}")
        else:
            print("   ❌ No se pudo obtener información de la base de datos")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n✅ Prueba completada")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    print(traceback.format_exc())
