"""
Script para limpiar totalmente la base de datos en Railway, centrándose especialmente en 
eliminar los productos problemáticos que persisten en las búsquedas.

Este script limpia las tablas principales y luego realiza una eliminación directa
de los productos problemáticos específicos por nombre y código.
"""

import os
import sys
import json
import psycopg2
import traceback
from datetime import datetime

# Productos problemáticos que queremos eliminar específicamente
PRODUCTOS_PROBLEMATICOS = [
    {"nombre": "PRODUCTO01", "codigo": "PROD002", "proveedor": "SICA"},
    {"nombre": "TERMICA 50a", "codigo": "TERM50A", "proveedor": "SICA"},
    {"nombre": "TERMICA 32A JELUZ", "codigo": "TERM32A", "proveedor": "JELUZ"}
]

def obtener_credenciales_railway():
    """Obtiene las credenciales de Railway desde el archivo railway.json"""
    try:
        if os.path.exists('railway.json'):
            with open('railway.json', 'r') as f:
                config = json.load(f)
                
                # Comprobar si hay URL directa o componentes separados
                if 'POSTGRES_URL' in config:
                    return {'url': config['POSTGRES_URL']}
                else:
                    return {
                        'host': config.get('PGHOST', ''),
                        'database': config.get('PGDATABASE', ''),
                        'user': config.get('PGUSER', ''),
                        'password': config.get('PGPASSWORD', ''),
                        'port': config.get('PGPORT', '')
                    }
        else:
            print("Archivo railway.json no encontrado")
            return None
    except Exception as e:
        print(f"Error al leer railway.json: {e}")
        return None

def conectar_db():
    """Establece conexión con la base de datos PostgreSQL en Railway"""
    config = obtener_credenciales_railway()
    if not config:
        print("No se pudieron obtener las credenciales de Railway")
        return None
    
    try:
        # Conectar usando URL o componentes
        if 'url' in config:
            url = config['url']
            # Asegurarse de que la URL tenga el formato correcto para psycopg2
            if url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql://')
            conn = psycopg2.connect(url)
        else:
            conn = psycopg2.connect(
                host=config.get('host'),
                database=config.get('database'),
                user=config.get('user'),
                password=config.get('password'),
                port=config.get('port')
            )
        
        print("Conexión establecida correctamente")
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        traceback.print_exc()
        return None

def verificar_tablas(conn):
    """Verifica qué tablas existen en la base de datos"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        print(f"Tablas existentes: {tablas}")
        return tablas
    except Exception as e:
        print(f"Error al verificar tablas: {e}")
        return []

def limpiar_tabla(conn, tabla):
    """Limpia todos los registros de una tabla específica"""
    try:
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            )
        """, (tabla,))
        tabla_existe = cursor.fetchone()[0]
        
        if not tabla_existe:
            print(f"La tabla {tabla} no existe, se omite")
            return {"exists": False}
        
        # Contar registros antes de limpiar
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count_before = cursor.fetchone()[0]
        
        # Eliminar todos los registros
        cursor.execute(f"DELETE FROM {tabla}")
        
        # Contar registros después de limpiar
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count_after = cursor.fetchone()[0]
        
        deleted = count_before - count_after
        print(f"Tabla {tabla}: {deleted} registros eliminados")
        
        return {
            "exists": True,
            "before": count_before,
            "after": count_after,
            "deleted": deleted
        }
    except Exception as e:
        print(f"Error al limpiar tabla {tabla}: {e}")
        return {"exists": True, "error": str(e)}

def eliminar_productos_especificos(conn):
    """Elimina productos específicos que han sido problemáticos"""
    if not conn:
        return {"success": False, "mensaje": "No hay conexión a la base de datos"}
    
    try:
        cursor = conn.cursor()
        resultados = []
        
        # Tablas donde buscar los productos
        tablas = ["productos_manual", "stock", "stock_history", "carrito"]
        
        for tabla in tablas:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                )
            """, (tabla,))
            tabla_existe = cursor.fetchone()[0]
            
            if not tabla_existe:
                print(f"La tabla {tabla} no existe, se omite")
                continue
            
            # Obtener las columnas de la tabla
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = %s
            """, (tabla,))
            columnas = [row[0] for row in cursor.fetchall()]
            
            # Verificar cuáles columnas podemos usar para la búsqueda
            columnas_nombre = [col for col in columnas if col.lower() in ["nombre", "producto", "descripcion"]]
            columnas_codigo = [col for col in columnas if col.lower() in ["codigo", "code", "sku"]]
            
            for producto in PRODUCTOS_PROBLEMATICOS:
                nombre = producto["nombre"]
                codigo = producto["codigo"]
                
                # Construir consultas de eliminación
                for col in columnas_nombre:
                    try:
                        cursor.execute(f"DELETE FROM {tabla} WHERE LOWER({col}) LIKE LOWER(%s)", (f"%{nombre}%",))
                        count = cursor.rowcount
                        if count > 0:
                            print(f"Eliminados {count} registros con nombre '{nombre}' de {tabla}.{col}")
                            resultados.append({
                                "tabla": tabla,
                                "columna": col,
                                "producto": nombre,
                                "eliminados": count
                            })
                    except Exception as e:
                        print(f"Error al eliminar por nombre en {tabla}.{col}: {e}")
                
                for col in columnas_codigo:
                    try:
                        cursor.execute(f"DELETE FROM {tabla} WHERE LOWER({col}) LIKE LOWER(%s)", (f"%{codigo}%",))
                        count = cursor.rowcount
                        if count > 0:
                            print(f"Eliminados {count} registros con código '{codigo}' de {tabla}.{col}")
                            resultados.append({
                                "tabla": tabla,
                                "columna": col,
                                "producto": codigo,
                                "eliminados": count
                            })
                    except Exception as e:
                        print(f"Error al eliminar por código en {tabla}.{col}: {e}")
        
        conn.commit()
        return resultados
    
    except Exception as e:
        print(f"Error al eliminar productos específicos: {e}")
        traceback.print_exc()
        conn.rollback()
        return []

def limpiar_tablas_railway():
    """Función principal que limpia todas las tablas relevantes en Railway"""
    print("="*80)
    print(f"INICIANDO LIMPIEZA DE BASE DE DATOS EN RAILWAY: {datetime.now()}")
    print("="*80)
    
    conn = conectar_db()
    if not conn:
        return {"success": False, "mensaje": "No se pudo conectar a la base de datos"}
    
    try:
        # 1. Verificar tablas existentes
        tablas = verificar_tablas(conn)
        
        # 2. Tablas a limpiar
        tablas_a_limpiar = [
            "productos_manual",  # Productos manuales
            "stock",             # Productos en stock
            "stock_history",     # Historial de stock
            "carrito"            # Productos en carrito
        ]
        
        # 3. Limpiar cada tabla
        resultados = {}
        for tabla in tablas_a_limpiar:
            if tabla in tablas:
                resultados[tabla] = limpiar_tabla(conn, tabla)
            else:
                print(f"La tabla {tabla} no existe")
                resultados[tabla] = {"exists": False}
        
        # 4. Eliminar productos específicos (como segunda capa de seguridad)
        print("\nEliminando productos problemáticos específicos...")
        productos_eliminados = eliminar_productos_especificos(conn)
        
        # 5. Confirmar cambios
        conn.commit()
        
        return {
            "success": True,
            "mensaje": "Base de datos limpiada correctamente",
            "tablas_limpiadas": [t for t in tablas_a_limpiar if t in tablas],
            "registros_eliminados": resultados,
            "productos_problematicos_eliminados": productos_eliminados
        }
    
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
        traceback.print_exc()
        conn.rollback()
        return {"success": False, "mensaje": f"Error: {str(e)}"}
    
    finally:
        if conn:
            conn.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    # Ejecutar la limpieza
    resultado = limpiar_tablas_railway()
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE LIMPIEZA")
    print("="*80)
    
    print(f"Éxito: {'Sí' if resultado.get('success') else 'No'}")
    print(f"Mensaje: {resultado.get('mensaje', '')}")
    
    if 'tablas_limpiadas' in resultado:
        print(f"\nTablas limpiadas: {', '.join(resultado['tablas_limpiadas'])}")
    
    if 'registros_eliminados' in resultado:
        print("\nRegistros eliminados:")
        for tabla, info in resultado['registros_eliminados'].items():
            if info.get('exists', True):
                if 'error' in info:
                    print(f"  - {tabla}: ERROR - {info['error']}")
                else:
                    print(f"  - {tabla}: {info.get('deleted', 0)} registros eliminados")
            else:
                print(f"  - {tabla}: No existe")
    
    if 'productos_problematicos_eliminados' in resultado:
        eliminados = resultado['productos_problematicos_eliminados']
        if eliminados:
            print(f"\nProductos problemáticos eliminados: {len(eliminados)} coincidencias")
            for item in eliminados:
                print(f"  - {item['producto']} en {item['tabla']}.{item['columna']}: {item['eliminados']} registros")
        else:
            print("\nNo se encontraron productos problemáticos para eliminar específicamente")
    
    print("\n" + "="*80)