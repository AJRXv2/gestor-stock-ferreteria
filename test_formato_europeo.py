"""
Script para probar la función de formato europeo
"""

def formatear_precio_europeo(precio):
    """
    Convierte un precio a formato europeo (puntos para miles, comas para decimales)
    Ej: 1234.56 -> "1.234,56"
    """
    try:
        # Convertir a float si es string
        if isinstance(precio, str):
            # Reemplazar comas por puntos para convertir correctamente
            precio = float(precio.replace(',', '.'))
        else:
            precio = float(precio)
        
        # Formatear el número con separador de miles como coma
        precio_formateado = "{:,.2f}".format(precio)
        
        # Cambiar comas por puntos (para miles) y punto por coma (para decimales)
        # Primero identificar la parte decimal (últimos 3 caracteres: .XX)
        if '.' in precio_formateado:
            partes = precio_formateado.rsplit('.', 1)  # Dividir por el último punto
            parte_entera = partes[0]
            parte_decimal = partes[1]
            
            # En la parte entera, cambiar comas por puntos
            parte_entera = parte_entera.replace(',', '.')
            
            # Reunir con coma como separador decimal
            return f"{parte_entera},{parte_decimal}"
        else:
            # Si no hay decimales, solo cambiar comas por puntos
            return precio_formateado.replace(',', '.')
    
    except (ValueError, TypeError):
        return str(precio)

# Probar diferentes casos
print('=== PRUEBAS DE FORMATO EUROPEO ===')

precios_test = [
    1234.56,
    123456.78,
    0.99,
    1000,
    15.5,
    '25.75',
    '1500,25',
    37754.69,
    12364.03
]

for precio in precios_test:
    resultado = formatear_precio_europeo(precio)
    print(f'{precio} -> {resultado}')

print('\n=== CASOS ESPECIALES ===')
print(f'None -> {formatear_precio_europeo(None)}')
print(f'"texto" -> {formatear_precio_europeo("texto")}')
print(f'0 -> {formatear_precio_europeo(0)}')