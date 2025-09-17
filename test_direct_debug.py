#!/usr/bin/env python3
"""Script directo para debuggear el problema de precios europeos"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from gestor import formatear_precio_europeo, buscar_multiples_codigos_excel, get_db_connection

def test_formatear_precio():
    """Test de la función formatear_precio_europeo"""
    print("=== TEST FORMATEAR PRECIO EUROPEO ===")
    casos = [
        0,
        0.0,
        None,
        '',
        '0',
        16839.84,
        '16839.84',
        19229.16996,
        1234.56
    ]
    
    for caso in casos:
        resultado = formatear_precio_europeo(caso)
        print(f"{repr(caso):15} -> {resultado}")
    print()

def test_buscar_excel():
    """Test búsqueda en Excel"""
    print("=== TEST BUSCAR EN EXCEL ===")
    
    # Códigos de prueba - usa códigos que sepas que podrían estar en tus Excel
    codigos_test = [
        '123456789',      # Código inexistente
        '999999999',      # Otro código inexistente
        '7790560046059',  # Código que podría existir
        '8042'            # Código simple
    ]
    
    for codigo in codigos_test:
        print(f"\n🔍 Buscando código: {codigo}")
        try:
            resultado = buscar_multiples_codigos_excel([codigo])
            print(f"📊 Resultado: {resultado}")
            
            if resultado and len(resultado) > 0:
                item = resultado[0]
                precio_raw = item.get('precio')
                precio_formato = formatear_precio_europeo(precio_raw)
                print(f"💰 Precio raw: {precio_raw}")
                print(f"💰 Precio formateado: {precio_formato}")
                print(f"📝 Nombre: {item.get('nombre')}")
                print(f"📁 Archivo: {item.get('archivo')}")
            else:
                print("❌ No encontrado en Excel")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_buscar_stock():
    """Test búsqueda en stock (BD)"""
    print("\n=== TEST BUSCAR EN STOCK (BD) ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener algunos productos de ejemplo
        cursor.execute("SELECT * FROM productos LIMIT 5")
        productos = cursor.fetchall()
        
        print(f"📊 Productos en BD: {len(productos)}")
        
        for producto in productos:
            print(f"\n📦 Producto: {producto}")
            if len(producto) >= 4:
                precio_raw = producto[3]
                precio_formato = formatear_precio_europeo(precio_raw)
                print(f"💰 Precio raw: {precio_raw}")
                print(f"💰 Precio formateado: {precio_formato}")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Error en BD: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 INICIANDO TESTS DE DEBUG")
    print("=" * 50)
    
    # Test 1: Formateo de precios
    test_formatear_precio()
    
    # Test 2: Búsqueda en stock
    test_buscar_stock()
    
    # Test 3: Búsqueda en Excel
    test_buscar_excel()
    
    print("=" * 50)
    print("✅ Tests completados")

if __name__ == "__main__":
    main()