import os
import sys

# Modificación para agregar JELUZ a PROVEEDOR_CONFIG en gestor.py

def agregar_jeluz_a_proveedor_config():
    """Agrega JELUZ a PROVEEDOR_CONFIG para solucionar el problema de búsqueda"""
    gestor_path = 'gestor.py'
    
    if not os.path.exists(gestor_path):
        print(f"Error: No se encontró el archivo {gestor_path}")
        return False
    
    try:
        # Leer el archivo gestor.py
        with open(gestor_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar dónde termina la definición de PROVEEDOR_CONFIG
        found_start = False
        found_end = False
        start_index = 0
        end_index = 0
        
        for i, line in enumerate(lines):
            if 'PROVEEDOR_CONFIG = {' in line:
                found_start = True
                start_index = i
            
            # Buscar el final de la definición (un corchete de cierre solo en la línea)
            if found_start and not found_end and line.strip() == '}':
                found_end = True
                end_index = i
                break
        
        if not found_start or not found_end:
            print("Error: No se pudo encontrar la definición de PROVEEDOR_CONFIG en el archivo")
            return False
        
        # Insertar la configuración de JELUZ antes del corchete de cierre
        jeluz_config = """    'jeluz': {
        'fila_encabezado': 0,
        'codigo': ['codigo', 'Codigo', 'CODIGO', 'cod', 'COD'],
        'producto': ['producto', 'Producto', 'PRODUCTO', 'descripcion', 'Descripcion', 'nombre', 'Nombre'],
        'precio': ['precio', 'Precio', 'PRECIO', 'p.venta', 'P.VENTA'],
        'dueno': 'ferreteria_general',
        'folder': 'ferreteria_general'
    },
"""
        
        # Insertar la configuración
        lines[end_index] = jeluz_config + lines[end_index]
        
        # Escribir el archivo modificado
        with open(gestor_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ JELUZ ha sido agregado correctamente a PROVEEDOR_CONFIG")
        return True
    
    except Exception as e:
        print(f"Error al modificar el archivo: {e}")
        return False

def modificar_buscar_en_excel():
    """Modificar la función buscar_en_excel para mejorar la búsqueda por proveedor"""
    gestor_path = 'gestor.py'
    
    if not os.path.exists(gestor_path):
        print(f"Error: No se encontró el archivo {gestor_path}")
        return False
    
    try:
        # Leer el archivo gestor.py
        with open(gestor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la función buscar_en_excel
        target_function = "def buscar_en_excel(termino_busqueda, proveedor_filtro=None, filtro_adicional=None, solo_ricky=False, solo_fg=False):"
        
        if target_function not in content:
            print("Error: No se encontró la función buscar_en_excel en el archivo")
            return False
        
        # Encontrar el bloque completo para reemplazar
        function_start = content.find(target_function)
        
        # Buscar el bloque de código que queremos modificar
        current_block = """    elif proveedor_filtro and proveedor_filtro in PROVEEDOR_CONFIG:
        # Nuevo: también incluir productos manuales que pertenezcan a ese proveedor Excel
        # Determinar alcance de dueños según flags
        if solo_ricky and not solo_fg:
            duenos_manual = ['ricky']
        elif solo_fg and not solo_ricky:
            duenos_manual = ['ferreteria_general']
        else:
            duenos_manual = ['ricky', 'ferreteria_general']
        for d in duenos_manual:
            resultados_manuales = buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, proveedor_filtro, dueno_filtro=d)
            if resultados_manuales:
                resultados.extend(resultados_manuales)"""
        
        # Nuevo bloque de código con la mejora
        new_block = """    elif proveedor_filtro and proveedor_filtro in PROVEEDOR_CONFIG:
        # Nuevo: también incluir productos manuales que pertenezcan a ese proveedor Excel
        # Determinar alcance de dueños según flags
        if solo_ricky and not solo_fg:
            duenos_manual = ['ricky']
        elif solo_fg and not solo_ricky:
            duenos_manual = ['ferreteria_general']
        else:
            duenos_manual = ['ricky', 'ferreteria_general']
        
        # Buscar tanto por el nombre del proveedor en Excel como por posibles variaciones en mayúsculas/minúsculas
        proveedor_nombre_original = proveedor_filtro
        
        # Intentar primero con el nombre exacto del proveedor
        for d in duenos_manual:
            resultados_manuales = buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, proveedor_nombre_original, dueno_filtro=d)
            if resultados_manuales:
                resultados.extend(resultados_manuales)
                
        # Si no hay resultados, probar con variaciones de mayúsculas/minúsculas
        if not resultados:
            print(f"[EXCEL DEBUG] No se encontraron resultados con el nombre exacto '{proveedor_nombre_original}', probando con versión en mayúsculas")
            proveedor_upper = proveedor_nombre_original.upper()
            if proveedor_upper != proveedor_nombre_original:
                for d in duenos_manual:
                    resultados_manuales = buscar_en_excel_manual_por_nombre_proveedor(termino_busqueda, proveedor_upper, dueno_filtro=d)
                    if resultados_manuales:
                        resultados.extend(resultados_manuales)"""
        
        # Reemplazar el bloque de código
        new_content = content.replace(current_block, new_block)
        
        # Escribir el archivo modificado
        with open(gestor_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ La función buscar_en_excel ha sido modificada correctamente")
        return True
    
    except Exception as e:
        print(f"Error al modificar el archivo: {e}")
        return False

if __name__ == "__main__":
    print("Solucionando problema de búsqueda para JELUZ")
    print("===========================================")
    
    # Agregar JELUZ a PROVEEDOR_CONFIG
    success1 = agregar_jeluz_a_proveedor_config()
    
    # Modificar la función buscar_en_excel
    success2 = modificar_buscar_en_excel()
    
    if success1 and success2:
        print("\n✅ ¡Todas las modificaciones se aplicaron correctamente!")
        print("Para que los cambios surtan efecto, es necesario reiniciar la aplicación.")
    else:
        print("\n❌ No se pudieron aplicar todas las modificaciones.")
        print("Revise los mensajes de error anteriores.")
    
    print("\nProceso completado.")