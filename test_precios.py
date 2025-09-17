#!/usr/bin/env python3
"""
Test script para verificar el formateo de precios europeos
"""

from gestor import buscar_multiples_codigos_excel, formatear_precio_europeo, extraer_codigo_de_barras

def test_formateo_precios():
    # Simular el flujo completo de procesar_escaneo
    codigo_barras_original = '8042'
    codigos_posibles = extraer_codigo_de_barras(codigo_barras_original, None)
    
    print('=== TEST FORMATEO PRECIOS EUROPEOS ===')
    print(f'Código de barras original: {codigo_barras_original}')
    print(f'Códigos extraídos: {codigos_posibles}')
    
    # Buscar en Excel
    todos_resultados_excel = buscar_multiples_codigos_excel(codigos_posibles, None)
    
    print(f'\n=== RESULTADOS DE EXCEL ===')
    print(f'Total encontrados: {len(todos_resultados_excel)}')
    
    productos_encontrados = []
    
    for item_excel in todos_resultados_excel:
        precio_original = item_excel.get('precio', 0)
        precio_formateado = formatear_precio_europeo(precio_original)
        
        print(f'\n--- Procesando item ---')
        print(f'Código: {item_excel.get("codigo", "")}')
        print(f'Nombre: {item_excel.get("nombre", "")[:50]}...')
        print(f'Precio original: {precio_original}')
        print(f'Precio formateado: {precio_formateado}')
        print(f'Proveedor: {item_excel.get("proveedor", "")}')
        print(f'Dueño: {item_excel.get("dueno", "")}')
        
        producto_excel = {
            'id': f'excel_{item_excel.get("codigo", "")}_{item_excel.get("proveedor", "")}',
            'codigo': item_excel.get('codigo', ''),
            'nombre': item_excel.get('nombre', ''),
            'precio': precio_original,
            'cantidad': 0,
            'proveedor': item_excel.get('proveedor', ''),
            'dueno': item_excel.get('dueno', ''),
            'codigo_extraido': item_excel.get('codigo_extraido', ''),
            'codigo_barras_original': codigo_barras_original,
            'source': 'excel',
            'en_stock': False,
            'precio_formato_europeo': precio_formateado
        }
        
        productos_encontrados.append(producto_excel)
        print(f'✅ Producto agregado con precio formateado: {producto_excel["precio_formato_europeo"]}')
    
    print(f'\n=== RESULTADO FINAL ===')
    print(f'Total productos: {len(productos_encontrados)}')
    
    # Simular la respuesta JSON
    respuesta = {
        'success': True,
        'message': f'Se encontraron {len(productos_encontrados)} producto(s)',
        'productos': productos_encontrados
    }
    
    print(f'\n=== RESPUESTA JSON SIMULADA ===')
    for i, p in enumerate(productos_encontrados, 1):
        print(f'{i}. {p["nombre"][:30]}...')
        print(f'   Precio: {p["precio"]}')
        print(f'   Precio formateado: {p["precio_formato_europeo"]}')
        print(f'   Source: {p["source"]}')
    
    return respuesta

if __name__ == '__main__':
    result = test_formateo_precios()
    
    # Verificar si hay productos sin formato europeo
    productos_sin_formato = [p for p in result['productos'] if not p.get('precio_formato_europeo') or p.get('precio_formato_europeo') == '0,00']
    
    if productos_sin_formato:
        print(f'\n❌ PROBLEMA: {len(productos_sin_formato)} producto(s) sin formato europeo correcto:')
        for p in productos_sin_formato:
            print(f'   - {p["nombre"][:30]}: precio={p["precio"]}, formato={p.get("precio_formato_europeo", "N/A")}')
    else:
        print(f'\n✅ ÉXITO: Todos los productos tienen formato europeo correcto!')