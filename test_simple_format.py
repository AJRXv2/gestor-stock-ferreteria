#!/usr/bin/env python3
"""Script minimalista para debuggear precios europeos"""

def formatear_precio_europeo(precio):
    """Función de formateo copiada directamente"""
    if precio is None or precio == '':
        return "0,00"
    
    try:
        # Convertir a float
        if isinstance(precio, str):
            precio = precio.replace(',', '.')
        precio_float = float(precio)
        
        # Si es 0, devolver "0,00"
        if precio_float == 0:
            return "0,00"
        
        # Formatear con 2 decimales
        precio_formateado = "{:.2f}".format(precio_float)
        
        # Separar parte entera y decimal
        partes = precio_formateado.split('.')
        parte_entera = partes[0]
        parte_decimal = partes[1]
        
        # Formatear parte entera con puntos como separadores de miles
        if len(parte_entera) > 3:
            # Invertir, agregar puntos cada 3 dígitos, e invertir de nuevo
            parte_entera_invertida = parte_entera[::-1]
            with_dots = '.'.join([parte_entera_invertida[i:i+3] for i in range(0, len(parte_entera_invertida), 3)])
            parte_entera = with_dots[::-1]
        
        return f"{parte_entera},{parte_decimal}"
        
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error al formatear precio '{precio}': {e}")
        return "0,00"

def test_formateo():
    """Test de formateo básico"""
    print("=== TEST FORMATEO EUROPEO ===")
    casos = [
        0,
        0.0,
        None,
        '',
        '0',
        16839.84,
        '16839.84',
        19229.16996,
        1234.56,
        123456.789
    ]
    
    for caso in casos:
        resultado = formatear_precio_europeo(caso)
        print(f"{repr(caso):15} -> {resultado}")

if __name__ == "__main__":
    test_formateo()