"""
Script de instalación para la migración de productos manuales de Excel a base de datos.
"""

import os
import subprocess
import sys

def get_python_command():
    """Obtiene el comando de Python a utilizar"""
    # En algunos sistemas puede ser 'python' o 'python3'
    if os.name == 'nt':  # Windows
        return 'python'
    else:  # Linux/Mac
        return 'python3'

def run_script(script_path, desc):
    """Ejecuta un script de Python y maneja errores"""
    print(f"\n====== EJECUTANDO: {desc} ======")
    python_cmd = get_python_command()
    
    try:
        result = subprocess.run([python_cmd, script_path], check=True)
        if result.returncode == 0:
            print(f"✅ {desc} completado exitosamente")
            return True
        else:
            print(f"❌ Error ejecutando {script_path}. Código de salida: {result.returncode}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    """Función principal que ejecuta todos los pasos de la migración"""
    print("="*50)
    print("  MIGRACIÓN DE PRODUCTOS MANUALES DE EXCEL A BASE DE DATOS")
    print("="*50)
    print("\nEste script realizará los siguientes pasos:")
    print("1. Migrar los datos del archivo Excel a la tabla productos_manual")
    print("2. Actualizar las funciones de búsqueda para usar la base de datos")
    print("3. Actualizar las funciones de agregar productos para usar la base de datos")
    print("4. Actualizar las funciones de eliminación para usar la base de datos")
    
    # Confirmar antes de continuar
    confirm = input("\n¿Desea continuar con la migración? (s/n): ")
    if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Migración cancelada por el usuario.")
        return
    
    # Migración de datos
    if not run_script('migrate_productos_manual.py', "Migración de datos"):
        print("\n❌ Error en el paso de migración de datos. Abortando el proceso.")
        return
    
    # Actualización de funciones de búsqueda
    if not run_script('update_search_functions.py', "Actualización de funciones de búsqueda"):
        print("\n❌ Error actualizando las funciones de búsqueda. Abortando el proceso.")
        return
    
    # Actualización de funciones de agregar productos
    if not run_script('update_product_functions.py', "Actualización de funciones de agregar productos"):
        print("\n❌ Error actualizando las funciones de agregar productos. Abortando el proceso.")
        return
    
    # Actualización de funciones de eliminación
    if not run_script('update_delete_functions.py', "Actualización de funciones de eliminación"):
        print("\n❌ Error actualizando las funciones de eliminación. Abortando el proceso.")
        return
    
    print("\n"+"="*50)
    print("  ✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*50)
    print("\nLos productos manuales ahora se almacenan en la base de datos.")
    print("El archivo Excel se seguirá actualizando como respaldo.")
    print("\nRecomendaciones:")
    print("1. Reinicie la aplicación para que los cambios surtan efecto.")
    print("2. Realice pruebas de búsqueda y agregación de productos manuales.")
    print("3. Verifique que los productos existentes aparezcan correctamente.")

if __name__ == "__main__":
    main()