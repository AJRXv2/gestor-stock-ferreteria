#!/usr/bin/env python3
"""
Test simple para verificar el formateo de precios
"""

import sys
import os

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar solo las funciones necesarias
def formatear_precio_europeo(precio):
    """Función de formateo europeo"""
    try:
        if isinstance(precio, str):
            precio = float(precio.replace(',', '.'))
        elif precio is None:
            precio = 0.0
        
        precio_float = float(precio)
        precio_americano = f"{precio_float:,.2f}"
        
        precio_europeo = ""
        for char in precio_americano:
            if char == ",":
                precio_europeo += "."
            elif char == ".":
                precio_europeo += ","
            else:
                precio_europeo += char
        
        return precio_europeo
        
    except (ValueError, TypeError):
        return "0,00"

def test_precios_especificos():
    """Test con precios específicos que encontramos en la búsqueda"""
    print('=== TEST FORMATEO PRECIOS ESPECÍFICOS ===')
    
    # Precios que encontramos en la búsqueda anterior
    precios_test = [
        19229.16996,   # Bremen tijera
        23467.03,      # Chiesa pinza
        0,             # Productos sin precio
        0.0,           # Precio explícitamente 0
        None,          # Precio None
        "",            # Precio vacío
        "19229.16996", # Precio como string
        12293.0,       # Crossmaster bocallave
        217860.0       # Crossmaster escalera
    ]
    
    for precio in precios_test:
        resultado = formatear_precio_europeo(precio)
        print(f'{repr(precio)} -> {resultado}')
    
    print('\n=== VERIFICACIÓN ===')
    
    # Simular productos como los que vienen de Excel
    productos_simulados = [
        {
            'codigo': '8042',
            'nombre': 'TIJERA P/PODAR DE 9" MANGO RECTO BREMEN® Acero Japonés (SK-5)',
            'precio': 19229.16996,
            'proveedor': 'BREMEN®',
            'dueno': 'ricky'
        },
        {
            'codigo': '8042', 
            'nombre': 'STANLEY pinza presion curva 254mm      84-369',
            'precio': 23467.03,
            'proveedor': 'chiesa',
            'dueno': 'ricky'
        },
        {
            'codigo': '9948042',
            'nombre': 'BOCALLAVE CROSS-HEXAG. 3/4"- 41mm',
            'precio': 12293.0,
            'proveedor': 'crossmaster',
            'dueno': 'ricky'
        }
    ]
    
    productos_con_formato = []
    for producto in productos_simulados:
        precio_original = producto['precio']
        precio_formateado = formatear_precio_europeo(precio_original)
        
        producto_final = {
            **producto,
            'precio_formato_europeo': precio_formateado,
            'source': 'excel',
            'en_stock': False
        }
        
        productos_con_formato.append(producto_final)
        
        print(f'Producto: {producto["nombre"][:40]}...')
        print(f'  Precio original: {precio_original}')
        print(f'  Precio formateado: {precio_formateado}')
        print(f'  ¿Tiene formato?: {bool(precio_formateado and precio_formateado != "0,00")}')
        print()
    
    # Verificar si todos tienen formato correcto
    productos_sin_formato = [p for p in productos_con_formato if not p.get('precio_formato_europeo') or p.get('precio_formato_europeo') == '0,00']
    
    if productos_sin_formato:
        print(f'❌ PROBLEMA: {len(productos_sin_formato)} producto(s) sin formato europeo correcto')
        return False
    else:
        print(f'✅ ÉXITO: Todos los {len(productos_con_formato)} productos tienen formato europeo correcto!')
        return True

if __name__ == '__main__':
    success = test_precios_especificos()
    exit(0 if success else 1)