import os
import re
import sqlite3

# Obtener ruta del archivo gestor.py en el directorio actual
ruta_gestor = os.path.join(os.getcwd(), 'gestor.py')

def normalizar_busqueda_proveedor():
    """
    Modifica la función buscar_en_excel para normalizar el nombre del proveedor
    y hacer búsquedas case-insensitive en PROVEEDOR_CONFIG
    """
    print("Iniciando normalización de búsqueda por proveedor...")
    
    # Leer el contenido actual del archivo
    with open(ruta_gestor, 'r', encoding='utf-8') as file:
        contenido = file.read()
    
    # Buscar el patrón de la función buscar_en_excel
    patron_funcion = r'def buscar_en_excel\(termino_busqueda, proveedor_filtro=None, filtro_adicional=None, solo_ricky=False, solo_fg=False\):(.*?)def '
    match = re.search(patron_funcion, contenido, re.DOTALL)
    
    if not match:
        print("⚠️ No se encontró la función buscar_en_excel. Verificar el archivo gestor.py")
        return False
    
    # Obtener el código actual de la función
    codigo_original = match.group(0)
    codigo_funcion = match.group(1)
    
    # Verificar si ya está normalizado
    if "proveedor_filtro = proveedor_filtro.lower() if proveedor_filtro else None" in codigo_funcion:
        print("✅ La normalización ya está aplicada.")
        return False
    
    # Buscar la línea de inicio para insertar nuestras modificaciones
    lineas = codigo_funcion.split('\n')
    indice_inicio = None
    
    for i, linea in enumerate(lineas):
        if "print(f\"🔍 [BUSCAR_EXCEL] Iniciando búsqueda:" in linea:
            indice_inicio = i
            break
    
    if indice_inicio is None:
        print("⚠️ No se encontró el punto de inserción adecuado.")
        return False
    
    # Insertar normalización después de la línea de inicio
    lineas.insert(indice_inicio + 1, "    # Normalizar el proveedor_filtro a minúsculas para comparaciones case-insensitive")
    lineas.insert(indice_inicio + 2, "    proveedor_filtro = proveedor_filtro.lower() if proveedor_filtro else None")
    
    # Ahora modificamos la comparación con PROVEEDOR_CONFIG para hacerla case-insensitive
    for i, linea in enumerate(lineas):
        # Modificar la primera condición donde se verifica si el proveedor está en PROVEEDOR_CONFIG
        if "elif proveedor_filtro and proveedor_filtro in PROVEEDOR_CONFIG:" in linea:
            lineas[i] = "    elif proveedor_filtro and proveedor_filtro in [k.lower() for k in PROVEEDOR_CONFIG.keys()]:"
            # Agregar código para obtener la clave original
            lineas.insert(i + 1, "        # Obtener la clave original del diccionario (preservando mayúsculas)")
            lineas.insert(i + 2, "        proveedor_key = next((k for k in PROVEEDOR_CONFIG.keys() if k.lower() == proveedor_filtro), proveedor_filtro)")
        
        # Modificar la condición donde se accede al PROVEEDOR_CONFIG después de la normalización
        if "proveedor_config = PROVEEDOR_CONFIG.get(proveedor_filtro, {})" in linea:
            lineas[i] = "            proveedor_key = next((k for k in PROVEEDOR_CONFIG.keys() if k.lower() == proveedor_filtro), proveedor_filtro)"
            lineas.insert(i + 1, "            proveedor_config = PROVEEDOR_CONFIG.get(proveedor_key, {})")
        
        # Modificar la segunda condición donde se verifica si el proveedor está en PROVEEDOR_CONFIG
        if "if not proveedor_filtro or proveedor_filtro in PROVEEDOR_CONFIG:" in linea:
            lineas[i] = "    if not proveedor_filtro or proveedor_filtro in [k.lower() for k in PROVEEDOR_CONFIG.keys()]:"
    
    # Reconstruir la función con las modificaciones
    codigo_modificado = '\n'.join(lineas)
    nuevo_codigo_funcion = f"def buscar_en_excel(termino_busqueda, proveedor_filtro=None, filtro_adicional=None, solo_ricky=False, solo_fg=False):{codigo_modificado}def "
    
    # Reemplazar la función original en el contenido completo
    contenido_actualizado = contenido.replace(codigo_original, nuevo_codigo_funcion)
    
    # Guardar los cambios
    with open(ruta_gestor, 'w', encoding='utf-8') as file:
        file.write(contenido_actualizado)
    
    print("✅ Normalización aplicada correctamente.")
    return True

def modificar_busqueda_en_excel_proveedor():
    """
    Modifica la función buscar_en_excel_proveedor para usar la clave normalizada del proveedor
    """
    print("Modificando función buscar_en_excel_proveedor...")
    
    # Leer el contenido actual del archivo
    with open(ruta_gestor, 'r', encoding='utf-8') as file:
        contenido = file.read()
    
    # Buscar el patrón de la función buscar_en_excel_proveedor
    patron_funcion = r'def buscar_en_excel_proveedor\(termino_busqueda, proveedor, filtro_adicional=None\):(.*?)def '
    match = re.search(patron_funcion, contenido, re.DOTALL)
    
    if not match:
        print("⚠️ No se encontró la función buscar_en_excel_proveedor. Verificar el archivo gestor.py")
        return False
    
    # Obtener el código actual de la función
    codigo_original = match.group(0)
    codigo_funcion = match.group(1)
    
    # Verificar si ya está normalizado
    if "proveedor_key = next((k for k in PROVEEDOR_CONFIG.keys()" in codigo_funcion:
        print("✅ La normalización ya está aplicada en buscar_en_excel_proveedor.")
        return False
    
    # Buscar la línea donde se accede a la configuración del proveedor
    lineas = codigo_funcion.split('\n')
    indice_config = None
    
    for i, linea in enumerate(lineas):
        if "config = PROVEEDOR_CONFIG.get(proveedor, {})" in linea:
            indice_config = i
            break
    
    if indice_config is None:
        print("⚠️ No se encontró el punto de inserción adecuado en buscar_en_excel_proveedor.")
        return False
    
    # Modificar el acceso a la configuración del proveedor
    lineas[indice_config] = "    # Normalizar el proveedor para búsqueda case-insensitive"
    lineas.insert(indice_config + 1, "    proveedor_lower = proveedor.lower() if proveedor else ''")
    lineas.insert(indice_config + 2, "    proveedor_key = next((k for k in PROVEEDOR_CONFIG.keys() if k.lower() == proveedor_lower), proveedor)")
    lineas.insert(indice_config + 3, "    config = PROVEEDOR_CONFIG.get(proveedor_key, {})")
    
    # Reconstruir la función con las modificaciones
    codigo_modificado = '\n'.join(lineas)
    nuevo_codigo_funcion = f"def buscar_en_excel_proveedor(termino_busqueda, proveedor, filtro_adicional=None):{codigo_modificado}def "
    
    # Reemplazar la función original en el contenido completo
    contenido_actualizado = contenido.replace(codigo_original, nuevo_codigo_funcion)
    
    # Guardar los cambios
    with open(ruta_gestor, 'w', encoding='utf-8') as file:
        file.write(contenido_actualizado)
    
    print("✅ Modificación aplicada correctamente a buscar_en_excel_proveedor.")
    return True

def aplicar_correcciones():
    """Aplicar todas las correcciones necesarias"""
    print("=== APLICANDO CORRECCIONES AL FILTRADO POR PROVEEDOR ===")
    
    # Modificar la función buscar_en_excel para normalizar el proveedor
    normalizar_busqueda_proveedor()
    
    # Modificar la función buscar_en_excel_proveedor para usar la clave normalizada
    modificar_busqueda_en_excel_proveedor()
    
    print("\n=== CORRECCIONES COMPLETADAS ===")
    print("✅ El filtrado por proveedor ahora debería funcionar correctamente.")
    print("✅ Se agregó normalización case-insensitive para la búsqueda de proveedores.")
    print("ℹ️ Ejecute nuevamente el diagnóstico para verificar las correcciones.")

if __name__ == "__main__":
    aplicar_correcciones()