import os

# Corrección para el error de sintaxis en PROVEEDOR_CONFIG

def corregir_sintaxis():
    """Corrige el error de sintaxis en PROVEEDOR_CONFIG"""
    gestor_path = 'gestor.py'
    
    if not os.path.exists(gestor_path):
        print(f"Error: No se encontró el archivo {gestor_path}")
        return False
    
    try:
        # Leer el archivo gestor.py
        with open(gestor_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar línea con error (doble llave de cierre)
        for i, line in enumerate(lines):
            if line.strip() == '},':
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                if next_line == '}':
                    # Eliminar la línea con la llave de cierre extra
                    lines[i] = line.replace('},', '}')
                    # Eliminar la línea siguiente que contiene solo }
                    lines.pop(i+1)
                    print(f"✅ Corregido error de sintaxis en la línea {i+1}")
                    break
        
        # Escribir el archivo corregido
        with open(gestor_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Archivo corregido correctamente")
        return True
    
    except Exception as e:
        print(f"Error al corregir el archivo: {e}")
        return False

if __name__ == "__main__":
    print("Corrigiendo error de sintaxis en PROVEEDOR_CONFIG")
    print("================================================")
    
    success = corregir_sintaxis()
    
    if success:
        print("\n✅ Archivo corregido exitosamente.")
    else:
        print("\n❌ No se pudo corregir el archivo.")
    
    print("\nProceso completado.")