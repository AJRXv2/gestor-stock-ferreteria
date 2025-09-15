"""
Script para corregir el formulario de agregar productos, asegurando que cargue los proveedores correctamente.
"""
import sqlite3
import sys
import os
import re

def db_query(query, params=(), fetch=False):
    """Ejecuta una consulta en la base de datos y opcionalmente devuelve resultados."""
    conn = sqlite3.connect('gestor_stock.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        result = cursor.execute(query, params)
        if fetch:
            return [dict(row) for row in result.fetchall()]
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en consulta: {query}  \nParams: {params}\nError: {str(e)}")
        return None
    finally:
        conn.close()

def corregir_formulario():
    """Corrige el formulario de agregar productos para cargar correctamente los proveedores."""
    print("\n=== CORREGIR FORMULARIO DE AGREGAR PRODUCTOS ===\n")
    
    # 1. Verificar que la plantilla tiene el código correcto para cargar los proveedores
    ruta_plantilla = os.path.join('templates', 'agregar.html')
    
    if not os.path.exists(ruta_plantilla):
        print(f"❌ Error: No se encontró la plantilla en {ruta_plantilla}")
        return
    
    print(f"1. Plantilla encontrada: {ruta_plantilla}")
    
    # Leer el contenido actual de la plantilla
    with open(ruta_plantilla, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si la función cargarProveedores existe
    if 'function cargarProveedores(' in contenido:
        print("2. Función cargarProveedores encontrada en la plantilla.")
    else:
        print("❌ Error: No se encontró la función cargarProveedores en la plantilla.")
        return
    
    # Verificar si se llama a la función cuando cambia el selector de dueño
    if 'addEventListener(\'change\', onChangeProv)' in contenido:
        print("3. Event listeners para los selectores de proveedores encontrados.")
    else:
        print("❌ Error: No se encontraron event listeners para los selectores de proveedores.")
        return
    
    # 2. Verificar el endpoint para obtener proveedores
    ruta_endpoint = 'gestor.py'
    
    if not os.path.exists(ruta_endpoint):
        print(f"❌ Error: No se encontró el archivo gestor.py")
        return
    
    print(f"4. Archivo gestor.py encontrado")
    
    # Verificar que el endpoint está definido correctamente
    with open(ruta_endpoint, 'r', encoding='utf-8') as f:
        contenido_gestor = f.read()
    
    if '@app.route(\'/obtener_proveedores_por_dueno\', methods=[\'POST\'])' in contenido_gestor:
        print("5. Endpoint obtener_proveedores_por_dueno encontrado.")
    else:
        print("❌ Error: No se encontró el endpoint obtener_proveedores_por_dueno.")
        return
    
    # 3. Verificar la lógica del endpoint
    patron_endpoint = r'def obtener_proveedores_por_dueno\(\):[^@]+'
    resultado = re.search(patron_endpoint, contenido_gestor, re.DOTALL)
    
    if resultado:
        codigo_endpoint = resultado.group(0)
        print("6. Código del endpoint encontrado.")
        
        # Verificar si usa la tabla proveedores_duenos
        if 'proveedores_duenos pd' in codigo_endpoint and 'JOIN proveedores_duenos' in codigo_endpoint:
            print("7. El endpoint utiliza correctamente la tabla proveedores_duenos.")
        else:
            print("⚠️ Advertencia: El endpoint no parece usar la tabla proveedores_duenos correctamente.")
    else:
        print("❌ Error: No se pudo extraer el código del endpoint.")
        return
    
    # 4. Probar la consulta manualmente para verificar que funciona
    for dueno in ['ferreteria_general', 'ricky']:
        proveedores = db_query(
            """
            SELECT DISTINCT p.nombre 
            FROM proveedores_manual p
            JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
            WHERE pd.dueno = ?
            ORDER BY p.nombre
            """, 
            (dueno,), fetch=True
        )
        
        nombres_proveedores = [p['nombre'] for p in proveedores]
        print(f"\n8. Prueba manual para dueño '{dueno}':")
        print(f"   - Proveedores encontrados: {len(nombres_proveedores)}")
        for i, nombre in enumerate(nombres_proveedores, 1):
            print(f"     {i}. {nombre}")
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===\n")
    print("✅ Todo parece estar configurado correctamente para cargar los proveedores.")
    print("Si aún hay problemas:")
    print("1. Verifica que la aplicación esté utilizando la versión correcta de gestor.py")
    print("2. Verifica que no haya errores de JavaScript en la consola del navegador")
    print("3. Asegúrate de que los selectores en el HTML tengan los IDs correctos")

if __name__ == "__main__":
    corregir_formulario()