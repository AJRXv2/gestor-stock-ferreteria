#!/usr/bin/env python3
"""
Debug específico para el código 7044 que aparece con precio 0,00
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del gestor
from gestor import (
    buscar_multiples_codigos_excel, 
    formatear_precio_europeo, 
    extraer_codigo_de_barras,
    parse_price,
    buscar_en_excel
)

def debug_codigo_7044():
    """Debug completo para el código 7044"""
    print("🔍 DEBUG CÓDIGO 7044")
    print("=" * 50)
    
    codigo_barras = "7795163070443"  # El código que probaste
    print(f"📱 Código de barras original: {codigo_barras}")
    
    # 1. Extraer códigos posibles
    codigos_extraidos = extraer_codigo_de_barras(codigo_barras, None)
    print(f"\n📋 Códigos extraídos: {codigos_extraidos}")
    
    # 2. Buscar usando buscar_multiples_codigos_excel
    print(f"\n🔍 Buscando con buscar_multiples_codigos_excel...")
    resultados = buscar_multiples_codigos_excel(codigos_extraidos, None)
    
    print(f"\n📊 Resultados encontrados: {len(resultados)}")
    for i, resultado in enumerate(resultados, 1):
        print(f"\n--- Resultado {i} ---")
        print(f"Código: {resultado.get('codigo')}")
        print(f"Nombre: {resultado.get('nombre')}")
        print(f"Precio raw: {repr(resultado.get('precio'))}")
        print(f"Precio texto: {repr(resultado.get('precio_texto'))}")
        print(f"Proveedor: {resultado.get('proveedor')}")
        print(f"Precio formato europeo: {repr(resultado.get('precio_formato_europeo'))}")
    
    # 3. Probar buscar_en_excel directamente con código específico
    print(f"\n🎯 Probando buscar_en_excel directamente con código '7044'...")
    resultados_directo = buscar_en_excel("7044", None, None, False, False)
    
    print(f"\n📊 Resultados directos encontrados: {len(resultados_directo)}")
    for i, resultado in enumerate(resultados_directo, 1):
        print(f"\n--- Resultado directo {i} ---")
        print(f"Código: {resultado.get('codigo')}")
        print(f"Nombre: {resultado.get('nombre')}")
        print(f"Precio raw: {repr(resultado.get('precio'))}")
        print(f"Precio texto: {repr(resultado.get('precio_texto'))}")
        print(f"Proveedor: {resultado.get('proveedor')}")
        precio_formateado = formatear_precio_europeo(resultado.get('precio', 0))
        print(f"Precio formateado manual: {precio_formateado}")
        print(f"Precio formato europeo campo: {repr(resultado.get('precio_formato_europeo'))}")
    
    # 4. Probar parse_price con diferentes valores
    print(f"\n🧪 Probando parse_price...")
    test_prices = ["0", "0.0", "", None, "16.839,84", "16839.84", "16,839.84"]
    for test_price in test_prices:
        parsed, error = parse_price(test_price)
        formatted = formatear_precio_europeo(parsed)
        print(f"  {repr(test_price)} -> {parsed} -> {formatted} (error: {error})")

if __name__ == "__main__":
    debug_codigo_7044()