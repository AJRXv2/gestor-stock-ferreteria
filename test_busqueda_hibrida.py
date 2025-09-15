#!/usr/bin/env python3
"""
Script de prueba para verificar que la búsqueda híbrida funciona correctamente
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import buscar_en_excel, PROVEEDOR_CONFIG
    
    print("🔍 Probando búsqueda híbrida (Excel + Base de datos)...")
    
    # Mostrar configuración de proveedores
    print(f"\n📋 Proveedores configurados:")
    for proveedor, config in PROVEEDOR_CONFIG.items():
        print(f"   - {proveedor}: {config.get('dueno')} (carpeta: {config.get('folder')})")
    
    # Probar búsqueda en proveedor específico (Excel)
    print(f"\n1. Búsqueda en proveedor 'chiesa' (debería buscar en Excel):")
    resultados = buscar_en_excel("CARBG7202", proveedor_filtro="chiesa")
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')}) - Fuente: {r.get('archivo', 'N/A')}")
    
    # Probar búsqueda en proveedor específico (Excel)
    print(f"\n2. Búsqueda en proveedor 'berger' (debería buscar en Excel):")
    resultados = buscar_en_excel("123", proveedor_filtro="berger")
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')}) - Fuente: {r.get('archivo', 'N/A')}")
    
    # Probar búsqueda solo para Ricky (debería buscar en Excel de Ricky)
    print(f"\n3. Búsqueda solo para Ricky (debería buscar en Excel de Ricky):")
    resultados = buscar_en_excel("test", solo_ricky=True)
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')}) - Fuente: {r.get('archivo', 'N/A')}")
    
    # Probar búsqueda solo para Ferretería General (debería buscar en Excel de FG)
    print(f"\n4. Búsqueda solo para Ferretería General (debería buscar en Excel de FG):")
    resultados = buscar_en_excel("test", solo_fg=True)
    print(f"   Resultados encontrados: {len(resultados)}")
    for r in resultados[:3]:
        print(f"   - {r.get('codigo')}: {r.get('nombre')} ({r.get('proveedor')}) - Fuente: {r.get('archivo', 'N/A')}")
    
    # Verificar que los archivos Excel existen
    print(f"\n5. Verificando archivos Excel:")
    for proveedor, config in PROVEEDOR_CONFIG.items():
        carpeta = config.get('folder', proveedor)
        ruta_carpeta = os.path.join('listas_excel', carpeta)
        if os.path.exists(ruta_carpeta):
            archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith('.xlsx') and not f.startswith('~')]
            print(f"   - {proveedor} ({carpeta}): {len(archivos)} archivos")
            for archivo in archivos[:2]:  # Mostrar solo los primeros 2
                print(f"     * {archivo}")
        else:
            print(f"   - {proveedor} ({carpeta}): ❌ Carpeta no existe")
    
    print("\n✅ Prueba completada")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    print(traceback.format_exc())
