import os
import re

# Obtener ruta del archivo gestor.py en el directorio actual
ruta_gestor = os.path.join(os.getcwd(), 'gestor.py')

def corregir_buscar_en_excel_proveedor():
    """Corregir la función buscar_en_excel_proveedor para normalizar el proveedor"""
    print("Corrigiendo buscar_en_excel_proveedor...")
    
    # Leer el contenido del archivo
    with open(ruta_gestor, 'r', encoding='utf-8') as file:
        contenido = file.read()
    
    # Buscar el código original donde se verifica la configuración del proveedor
    fragmento_original = """        # Verificar que exista la configuración del proveedor
        if proveedor not in PROVEEDOR_CONFIG:
            print(f"[EXCEL] Error: Proveedor '{proveedor}' no configurado")
            return []
        
        # Obtener configuración del proveedor
        config = PROVEEDOR_CONFIG[proveedor]"""
    
    # Código de reemplazo con normalización case-insensitive
    fragmento_nuevo = """        # Verificar que exista la configuración del proveedor (case-insensitive)
        proveedor_lower = proveedor.lower() if proveedor else ''
        
        # Verificar primero con la clave exacta
        if proveedor in PROVEEDOR_CONFIG:
            proveedor_key = proveedor
        # Si no existe, buscar de forma case-insensitive
        else:
            proveedor_key = next((k for k in PROVEEDOR_CONFIG.keys() if k.lower() == proveedor_lower), None)
            
        if not proveedor_key:
            print(f"[EXCEL] Error: Proveedor '{proveedor}' no configurado")
            return []
        
        # Obtener configuración del proveedor
        config = PROVEEDOR_CONFIG[proveedor_key]"""
    
    # Realizar el reemplazo
    if fragmento_original in contenido:
        contenido_nuevo = contenido.replace(fragmento_original, fragmento_nuevo)
        
        # Guardar los cambios
        with open(ruta_gestor, 'w', encoding='utf-8') as file:
            file.write(contenido_nuevo)
        
        print("✅ La función buscar_en_excel_proveedor ha sido corregida correctamente.")
        return True
    else:
        print("⚠️ No se encontró el fragmento exacto a reemplazar.")
        return False

if __name__ == "__main__":
    corregir_buscar_en_excel_proveedor()