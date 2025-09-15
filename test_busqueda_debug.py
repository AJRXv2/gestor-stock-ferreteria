#!/usr/bin/env python3
"""
Script para debuggear la búsqueda de productos
"""

import os
import sys

# Configurar para usar SQLite local
os.environ['USE_POSTGRES'] = '0'

def test_busqueda():
    """Prueba la función de búsqueda con debug detallado"""
    
    print("🔍 DEBUG DE BÚSQUEDA DE PRODUCTOS")
    print("=" * 40)
    
    try:
        from gestor import db_query, buscar_en_excel_manual_por_nombre_proveedor
        
        print("✅ Módulos importados correctamente")
        
        # Simular la búsqueda que debería funcionar
        termino = "CARBG7202"
        proveedor = "Chiesa"
        dueno = "ricky"
        
        print(f"\n🔍 Buscando:")
        print(f"   Término: '{termino}'")
        print(f"   Proveedor: '{proveedor}'")
        print(f"   Dueño: '{dueno}'")
        
        # Llamar a la función
        resultados = buscar_en_excel_manual_por_nombre_proveedor(termino, proveedor, dueno)
        
        print(f"\n📊 Resultados encontrados: {len(resultados)}")
        for i, resultado in enumerate(resultados):
            print(f"   {i+1}. {resultado}")
        
        # También probar sin filtro de dueño
        print(f"\n🔍 Buscando sin filtro de dueño:")
        resultados_sin_dueno = buscar_en_excel_manual_por_nombre_proveedor(termino, proveedor, None)
        print(f"📊 Resultados sin dueño: {len(resultados_sin_dueno)}")
        
        # Probar con diferentes variaciones del nombre del proveedor
        variaciones = ["chiesa", "CHIESA", "Chiesa", "CHIESA "]
        for var in variaciones:
            print(f"\n🔍 Probando con proveedor: '{var}'")
            resultados_var = buscar_en_excel_manual_por_nombre_proveedor(termino, var, dueno)
            print(f"📊 Resultados: {len(resultados_var)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_busqueda()
