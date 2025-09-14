import os
import importlib.util
import sys

# Cargar gestor.py como módulo
spec = importlib.util.spec_from_file_location("gestor", "gestor.py")
gestor = importlib.util.module_from_spec(spec)
sys.modules["gestor"] = gestor
spec.loader.exec_module(gestor)

def verificar_jeluz_en_proveedor_config():
    """Verificar si JELUZ está en PROVEEDOR_CONFIG"""
    print("\n=== VERIFICANDO JELUZ EN PROVEEDOR_CONFIG ===")
    
    if 'jeluz' in gestor.PROVEEDOR_CONFIG:
        print("✅ JELUZ encontrado en PROVEEDOR_CONFIG")
        jeluz_config = gestor.PROVEEDOR_CONFIG['jeluz']
        for key, value in jeluz_config.items():
            if key != 'codigo' and key != 'producto' and key != 'precio':  # Estos son muy largos
                print(f"  - {key}: {value}")
        return True
    else:
        print("❌ JELUZ NO encontrado en PROVEEDOR_CONFIG")
        return False

def probar_busqueda_term32a():
    """Probar la búsqueda del producto TERM32A con proveedor JELUZ"""
    print("\n=== PROBANDO BÚSQUEDA DE TERM32A CON PROVEEDOR JELUZ ===")
    
    # Probar diferentes variantes de nombre de proveedor
    variantes = ["jeluz", "JELUZ", "Jeluz"]
    
    for proveedor in variantes:
        print(f"\nProbando búsqueda con proveedor: '{proveedor}'")
        resultados = gestor.buscar_en_excel("TERM32A", proveedor, solo_fg=True)
        
        if resultados:
            print(f"✅ Se encontraron {len(resultados)} resultados")
            for i, prod in enumerate(resultados, 1):
                print(f"  Resultado {i}: Código={prod.get('codigo')}, Proveedor={prod.get('proveedor')}")
                
            # Verificar si TERM32A está en los resultados
            encontrado = False
            for prod in resultados:
                if prod.get('codigo') == 'TERM32A' and prod.get('proveedor', '').upper() == 'JELUZ':
                    encontrado = True
                    break
            
            if encontrado:
                print("✅ El producto TERM32A de JELUZ fue encontrado correctamente")
            else:
                print("❌ El producto TERM32A de JELUZ NO fue encontrado en los resultados")
        else:
            print("❌ No se encontraron resultados")

def probar_busqueda_sin_filtro():
    """Probar la búsqueda sin filtro de proveedor"""
    print("\n=== PROBANDO BÚSQUEDA SIN FILTRO DE PROVEEDOR ===")
    
    resultados = gestor.buscar_en_excel("TERM32A", None, solo_fg=True)
    
    if resultados:
        print(f"✅ Se encontraron {len(resultados)} resultados")
        for i, prod in enumerate(resultados, 1):
            print(f"  Resultado {i}: Código={prod.get('codigo')}, Proveedor={prod.get('proveedor')}")
    else:
        print("❌ No se encontraron resultados")

def revisar_codigo_buscar_en_excel():
    """Revisar el código actual de la función buscar_en_excel"""
    print("\n=== REVISANDO CÓDIGO DE BUSCAR_EN_EXCEL ===")
    
    # Obtener el código fuente de la función
    import inspect
    source = inspect.getsource(gestor.buscar_en_excel)
    
    print("Revisando patrones clave en el código:")
    
    if "proveedor_nombre_original = proveedor_filtro" in source:
        print("✅ Se encontró la variable proveedor_nombre_original")
    else:
        print("❌ No se encontró la variable proveedor_nombre_original")
    
    if "proveedor_upper = proveedor_nombre_original.upper()" in source:
        print("✅ Se encontró la conversión a mayúsculas")
    else:
        print("❌ No se encontró la conversión a mayúsculas")
    
    if "No se encontraron resultados con el nombre exacto" in source:
        print("✅ Se encontró el mensaje de diagnóstico")
    else:
        print("❌ No se encontró el mensaje de diagnóstico")

if __name__ == "__main__":
    print("=== TEST DE BÚSQUEDA PARA JELUZ Y TERM32A ===")
    
    # 1. Verificar PROVEEDOR_CONFIG
    verificar_jeluz_en_proveedor_config()
    
    # 2. Revisar el código de la función
    revisar_codigo_buscar_en_excel()
    
    # 3. Probar búsqueda con proveedor
    probar_busqueda_term32a()
    
    # 4. Probar búsqueda sin filtro
    probar_busqueda_sin_filtro()
    
    print("\n=== TEST COMPLETO ===")