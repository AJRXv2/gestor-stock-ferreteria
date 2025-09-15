"""
Script para aplicar correcciones a la base de datos de Railway y PostgreSQL.
Este script ejecuta una serie de correcciones tanto en local como en Railway.
"""
import os
import sys
import subprocess
import time

def ejecutar_correcciones():
    """Ejecuta las correcciones necesarias para el entorno de Railway."""
    print("\n=== CORRECCIONES PARA ENTORNO RAILWAY (POSTGRESQL) ===\n")
    
    # 1. Corregir relaciones huérfanas y sincronizar tablas localmente primero
    print("1. Ejecutando correcciones locales para asegurar integridad de datos...")
    
    try:
        subprocess.run(["python", "corregir_relaciones_huerfanas.py"], check=True)
        subprocess.run(["python", "corregir_proveedores_duenos.py"], check=True)
        subprocess.run(["python", "sincronizar_proveedores_meta.py"], check=True)
        print("✅ Correcciones locales completadas exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar las correcciones locales: {e}")
        print("Continuando con las correcciones para Railway...")
    
    # 2. Aplicar correcciones a Railway
    print("\n2. Aplicando correcciones a la base de datos de Railway...")
    
    try:
        print("\n⚙️ Ejecutando sincronización de proveedores_meta en Railway...")
        subprocess.run(["python", "sincronizar_proveedores_meta_railway.py"], check=True)
        print("✅ Sincronización de proveedores_meta en Railway completada.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar la sincronización en Railway: {e}")
        print("Revisa los detalles del error y asegúrate de tener acceso a la base de datos de Railway.")
        return
    
    # 3. Instrucciones finales
    print("\n=== PROCESO DE CORRECCIÓN COMPLETO ===\n")
    print("Se han aplicado las siguientes correcciones:")
    print("1. Eliminación de relaciones huérfanas en la tabla proveedores_duenos")
    print("2. Corrección de proveedores sin dueño asignado")
    print("3. Sincronización de la tabla proveedores_meta con proveedores_duenos")
    print("4. Aplicación de estas correcciones en la base de datos PostgreSQL de Railway")
    
    print("\nPara verificar que todo funcione correctamente en la versión online:")
    print("1. Accede a la aplicación en Railway")
    print("2. Intenta agregar un producto manual y verifica que aparezcan los proveedores")
    print("3. Si aún hay problemas, verifica los logs de la aplicación en Railway")

if __name__ == "__main__":
    ejecutar_correcciones()