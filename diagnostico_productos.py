"""
Diagnóstico para encontrar de dónde vienen los productos persistentes.
Examina tanto la base de datos como los posibles archivos Excel.
"""

import os
import pandas as pd
import json
import psycopg2
import psycopg2.extras
import sqlite3
from datetime import datetime

# Constantes
EXCEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listas_excel')
MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, 'productos_manual.xlsx')
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gestor_stock.db')

# Lista de productos problemáticos para buscar
PRODUCTOS_PROBLEMA = [
    {"nombre": "PRODUCTO01", "codigo": "PROD002", "proveedor": "SICA"},
    {"nombre": "TERMICA 50a", "codigo": "TERM50A", "proveedor": "SICA"},
    {"nombre": "TERMICA 32A JELUZ", "codigo": "TERM32A", "proveedor": "JELUZ"}
]

def is_railway():
    """Determina si estamos en Railway verificando las variables de entorno"""
    return bool(os.environ.get('RAILWAY_ENVIRONMENT', False))

def get_db_connection():
    """Establece una conexión a la base de datos según el entorno"""
    if is_railway() or os.path.exists('railway.json'):
        # Usar credenciales de Railway
        try:
            if is_railway():
                postgres_url = os.environ.get('DATABASE_URL', '')
            else:
                railway_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'railway.json')
                with open(railway_json, 'r') as f:
                    railway_config = json.load(f)
                
                # Obtener url de conexión de diferentes maneras
                postgres_url = railway_config.get('POSTGRES_URL', '')
                if not postgres_url:
                    # Intentar construir la URL de conexión a partir de componentes
                    pghost = railway_config.get('PGHOST', '')
                    pgdatabase = railway_config.get('PGDATABASE', '')
                    pguser = railway_config.get('PGUSER', '')
                    pgpassword = railway_config.get('PGPASSWORD', '')
                    pgport = railway_config.get('PGPORT', '')
                    
                    if all([pghost, pgdatabase, pguser, pgpassword, pgport]):
                        postgres_url = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
            
            if not postgres_url:
                raise ValueError("No se pudo obtener URL de conexión a PostgreSQL")
            
            if postgres_url.startswith('postgres://'):
                postgres_url = postgres_url.replace('postgres://', 'postgresql://')
                
            conn = psycopg2.connect(postgres_url)
            conn.cursor_factory = psycopg2.extras.DictCursor
            print("Conectado a PostgreSQL")
            return conn
        except Exception as e:
            print(f"Error conectando a PostgreSQL: {e}")
    
    # Si no estamos en Railway o hay un error, usar SQLite
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        print("Conectado a SQLite")
        return conn
    except Exception as e:
        print(f"Error conectando a SQLite: {e}")
    
    return None

def check_db_tables():
    """Examina las tablas en la base de datos para buscar los productos problemáticos"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        if is_railway() or os.path.exists('railway.json'):
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tablas en la base de datos: {tables}")
        
        # Verificar productos en todas las tablas relevantes
        tables_to_check = [
            "productos_manual",
            "stock",
            "stock_history",
            "carrito"
        ]
        
        encontrados = []
        
        for table in tables_to_check:
            if table not in tables:
                print(f"La tabla {table} no existe en la base de datos")
                continue
            
            print(f"\nBuscando en tabla: {table}")
            
            # Verificar la estructura de la tabla
            if is_railway() or os.path.exists('railway.json'):
                cursor.execute(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = '{table}';
                """)
            else:
                cursor.execute(f"PRAGMA table_info({table});")
                
            columns = [row[0] if is_railway() or os.path.exists('railway.json') else row[1] for row in cursor.fetchall()]
            print(f"Columnas en {table}: {columns}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Total de registros en {table}: {count}")
            
            # Si es la tabla stock, mostrar los primeros 10 registros para diagnóstico
            if table == "stock" and count > 0:
                print(f"\nPrimeros 10 registros en tabla stock:")
                if is_railway() or os.path.exists('railway.json'):
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                else:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                    
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        row_dict = dict(row)
                    else:
                        # Convertir Row a dict
                        row_dict = {columns[i]: row[i] for i in range(len(columns)) if i < len(row)}
                    print(f"  - {row_dict}")
            
            # Búsqueda más exhaustiva para cada producto problemático
            for producto in PRODUCTOS_PROBLEMA:
                nombre = producto.get("nombre", "")
                codigo = producto.get("codigo", "")
                proveedor = producto.get("proveedor", "")
                
                # 1. Buscar por igualdad exacta (case insensitive)
                where_clauses = []
                params = []
                
                # Mapear posibles nombres de columnas para cada propiedad
                nombre_columns = ["nombre", "producto", "descripcion", "name", "description"]
                codigo_columns = ["codigo", "code", "sku", "id_producto", "product_code"]
                proveedor_columns = ["proveedor", "proveedor_nombre", "supplier", "supplier_name"]
                
                # Construir claúsulas WHERE para cada columna posible
                for column in columns:
                    col_lower = column.lower()
                    
                    if any(c == col_lower for c in nombre_columns) and nombre:
                        if is_railway() or os.path.exists('railway.json'):
                            where_clauses.append(f"LOWER({column}) = LOWER(%s)")
                        else:
                            where_clauses.append(f"LOWER({column}) = LOWER(?)")
                        params.append(nombre)
                    
                    if any(c == col_lower for c in codigo_columns) and codigo:
                        if is_railway() or os.path.exists('railway.json'):
                            where_clauses.append(f"LOWER({column}) = LOWER(%s)")
                        else:
                            where_clauses.append(f"LOWER({column}) = LOWER(?)")
                        params.append(codigo)
                    
                    if any(c == col_lower for c in proveedor_columns) and proveedor:
                        if is_railway() or os.path.exists('railway.json'):
                            where_clauses.append(f"LOWER({column}) = LOWER(%s)")
                        else:
                            where_clauses.append(f"LOWER({column}) = LOWER(?)")
                        params.append(proveedor)
                
                if not where_clauses:
                    print(f"No se pueden buscar productos en {table} (columnas incompatibles)")
                    continue
                
                query = f"SELECT * FROM {table} WHERE {' OR '.join(where_clauses)}"
                cursor.execute(query, tuple(params))
                
                results = cursor.fetchall()
                if results:
                    print(f"¡ENCONTRADO EXACTO! Producto '{nombre}' ({codigo}) en tabla {table}: {len(results)} coincidencia(s)")
                    for row in results:
                        if isinstance(row, dict):
                            row_dict = dict(row)
                        else:
                            # Convertir Row a dict
                            row_dict = {columns[i]: row[i] for i in range(len(columns)) if i < len(row)}
                        
                        print(f"  - Datos: {row_dict}")
                        encontrados.append({
                            "tabla": table,
                            "producto": nombre,
                            "codigo": codigo,
                            "tipo_busqueda": "exacta",
                            "datos": row_dict
                        })
                else:
                    print(f"Producto '{nombre}' ({codigo}) NO encontrado con búsqueda exacta en tabla {table}")
                
                # 2. Buscar por coincidencia parcial (LIKE %término%)
                where_clauses = []
                params = []
                
                for column in columns:
                    col_lower = column.lower()
                    
                    if any(c == col_lower for c in nombre_columns) and nombre:
                        if is_railway() or os.path.exists('railway.json'):
                            where_clauses.append(f"LOWER({column}) LIKE LOWER(%s)")
                        else:
                            where_clauses.append(f"LOWER({column}) LIKE LOWER(?)")
                        params.append(f"%{nombre}%")
                    
                    if any(c == col_lower for c in codigo_columns) and codigo:
                        if is_railway() or os.path.exists('railway.json'):
                            where_clauses.append(f"LOWER({column}) LIKE LOWER(%s)")
                        else:
                            where_clauses.append(f"LOWER({column}) LIKE LOWER(?)")
                        params.append(f"%{codigo}%")
                
                if not where_clauses:
                    continue
                
                query = f"SELECT * FROM {table} WHERE {' OR '.join(where_clauses)}"
                cursor.execute(query, tuple(params))
                
                results = cursor.fetchall()
                if results:
                    print(f"¡ENCONTRADO PARCIAL! Producto '{nombre}' ({codigo}) en tabla {table}: {len(results)} coincidencia(s)")
                    for row in results:
                        if isinstance(row, dict):
                            row_dict = dict(row)
                        else:
                            # Convertir Row a dict
                            row_dict = {columns[i]: row[i] for i in range(len(columns)) if i < len(row)}
                        
                        print(f"  - Datos: {row_dict}")
                        encontrados.append({
                            "tabla": table,
                            "producto": nombre,
                            "codigo": codigo,
                            "tipo_busqueda": "parcial",
                            "datos": row_dict
                        })
                else:
                    print(f"Producto '{nombre}' ({codigo}) NO encontrado con búsqueda parcial en tabla {table}")
        
        return encontrados
    
    except Exception as e:
        print(f"Error examinando tablas: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def check_excel_files():
    """Examina los archivos Excel para buscar los productos problemáticos"""
    encontrados = []
    
    # 1. Verificar productos_manual.xlsx
    if os.path.exists(MANUAL_PRODUCTS_FILE):
        print(f"\nExaminando archivo: {MANUAL_PRODUCTS_FILE}")
        try:
            df = pd.read_excel(MANUAL_PRODUCTS_FILE)
            print(f"Registros en el archivo: {len(df)}")
            
            if not df.empty:
                # Normalizar nombres de columnas
                if 'Código' in df.columns:
                    df.rename(columns={'Código': 'Codigo'}, inplace=True)
                if 'Dueño' in df.columns:
                    df.rename(columns={'Dueño': 'Dueno'}, inplace=True)
                
                # Buscar productos problemáticos
                for producto in PRODUCTOS_PROBLEMA:
                    nombre = producto.get("nombre", "")
                    codigo = producto.get("codigo", "")
                    
                    # Buscar por nombre o código
                    mask = (
                        df['Nombre'].str.contains(nombre, case=False, na=False) |
                        df['Codigo'].str.contains(codigo, case=False, na=False)
                    ) if 'Nombre' in df.columns and 'Codigo' in df.columns else None
                    
                    if mask is not None:
                        matches = df[mask]
                        if not matches.empty:
                            print(f"¡ENCONTRADO! Producto '{nombre}' ({codigo}) en {MANUAL_PRODUCTS_FILE}: {len(matches)} coincidencia(s)")
                            print(matches)
                            encontrados.append({
                                "archivo": MANUAL_PRODUCTS_FILE,
                                "producto": nombre,
                                "codigo": codigo,
                                "datos": matches.to_dict('records')
                            })
                        else:
                            print(f"Producto '{nombre}' ({codigo}) NO encontrado en {MANUAL_PRODUCTS_FILE}")
        except Exception as e:
            print(f"Error examinando {MANUAL_PRODUCTS_FILE}: {e}")
    else:
        print(f"El archivo {MANUAL_PRODUCTS_FILE} no existe")
    
    # 2. Buscar en todos los archivos Excel en listas_excel y subcarpetas
    excel_count = 0
    for root, dirs, files in os.walk(EXCEL_FOLDER):
        for file in files:
            if file.endswith('.xlsx') and file != os.path.basename(MANUAL_PRODUCTS_FILE):
                excel_path = os.path.join(root, file)
                excel_count += 1
                
                print(f"\nExaminando archivo: {excel_path}")
                try:
                    df = pd.read_excel(excel_path)
                    print(f"Registros en el archivo: {len(df)}")
                    
                    if not df.empty:
                        # Buscar cualquier columna que pueda contener los productos
                        for producto in PRODUCTOS_PROBLEMA:
                            nombre = producto.get("nombre", "")
                            codigo = producto.get("codigo", "")
                            
                            # Buscar en todas las columnas posibles
                            found = False
                            for col in df.columns:
                                if df[col].dtype == object:  # Solo buscar en columnas de texto
                                    matches = df[df[col].astype(str).str.contains(nombre, case=False, na=False) | 
                                                df[col].astype(str).str.contains(codigo, case=False, na=False)]
                                    
                                    if not matches.empty:
                                        print(f"¡ENCONTRADO! Producto '{nombre}' ({codigo}) en {excel_path}, columna {col}: {len(matches)} coincidencia(s)")
                                        print(matches)
                                        encontrados.append({
                                            "archivo": excel_path,
                                            "producto": nombre,
                                            "codigo": codigo,
                                            "columna": col,
                                            "datos": matches.to_dict('records')
                                        })
                                        found = True
                            
                            if not found:
                                print(f"Producto '{nombre}' ({codigo}) NO encontrado en {excel_path}")
                except Exception as e:
                    print(f"Error examinando {excel_path}: {e}")
    
    print(f"\nTotal de archivos Excel examinados: {excel_count + 1} (incluyendo productos_manual.xlsx)")
    return encontrados

def check_search_functions():
    """Examina el código para identificar cómo se realizan las búsquedas"""
    print("\nAnalizando funciones de búsqueda en el código...")
    
    search_files = [
        "gestor.py",
        "update_search_functions.py",
        "buscar_productos_fix.py",
        "fix_jeluz_search.py",
        "buscar_en_bd.py"
    ]
    
    search_info = []
    
    for file in search_files:
        if not os.path.exists(file):
            print(f"Archivo {file} no encontrado")
            continue
            
        print(f"\nExaminando archivo de búsqueda: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Buscar patrones de búsqueda en el código
            search_patterns = [
                "SELECT", "FROM stock", "FROM productos_manual",
                "LIKE", "productos_manual.xlsx", "read_excel",
                "buscar", "search", "filtrar", "filter"
            ]
            
            results = {}
            for pattern in search_patterns:
                if pattern in content:
                    line_number = 1
                    lines_with_pattern = []
                    
                    for line in content.split('\n'):
                        if pattern in line:
                            lines_with_pattern.append((line_number, line.strip()))
                        line_number += 1
                    
                    results[pattern] = lines_with_pattern
                    
                    if lines_with_pattern:
                        print(f"Patrón '{pattern}' encontrado {len(lines_with_pattern)} veces en {file}")
                        for ln, line in lines_with_pattern[:3]:  # Mostrar solo las primeras 3 coincidencias
                            print(f"  - Línea {ln}: {line[:100]}...")
                        if len(lines_with_pattern) > 3:
                            print(f"  - Y {len(lines_with_pattern) - 3} coincidencias más...")
            
            search_info.append({
                "archivo": file,
                "patrones_encontrados": results
            })
            
        except Exception as e:
            print(f"Error analizando {file}: {e}")
    
    return search_info

def eliminar_productos_problema():
    """Intenta eliminar los productos problemáticos de todas las fuentes posibles"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos para eliminar productos")
        return False
    
    try:
        cursor = conn.cursor()
        eliminados = []
        
        print("\n=== INTENTANDO ELIMINACIÓN FORZADA DE PRODUCTOS PROBLEMÁTICOS ===")
        
        # Tablas donde podrían estar los productos
        tables_to_clean = [
            "productos_manual",
            "stock",
            "stock_history",
            "carrito"
        ]
        
        for table in tables_to_clean:
            # Verificar si la tabla existe
            if is_railway() or os.path.exists('railway.json'):
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = %s
                    )
                """, (table,))
                table_exists = cursor.fetchone()[0]
            else:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                table_exists = bool(cursor.fetchone())
            
            if not table_exists:
                print(f"La tabla {table} no existe, se omite")
                continue
            
            print(f"\nLimpiando tabla: {table}")
            
            # Obtener las columnas de la tabla
            if is_railway() or os.path.exists('railway.json'):
                cursor.execute(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = '{table}';
                """)
                columns = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
            
            # Identificar columnas para búsqueda
            nombre_columns = [col for col in columns if col.lower() in ["nombre", "producto", "descripcion"]]
            codigo_columns = [col for col in columns if col.lower() in ["codigo", "code", "sku"]]
            
            # Para cada producto problemático
            for producto in PRODUCTOS_PROBLEMA:
                nombre = producto.get("nombre", "")
                codigo = producto.get("codigo", "")
                
                # Construir cláusulas WHERE para eliminar por nombre o código
                where_clauses = []
                
                for col in nombre_columns:
                    if is_railway() or os.path.exists('railway.json'):
                        where_clauses.append(f"LOWER({col}) LIKE LOWER(%s)")
                    else:
                        where_clauses.append(f"LOWER({col}) LIKE LOWER(?)")
                
                for col in codigo_columns:
                    if is_railway() or os.path.exists('railway.json'):
                        where_clauses.append(f"LOWER({col}) LIKE LOWER(%s)")
                    else:
                        where_clauses.append(f"LOWER({col}) LIKE LOWER(?)")
                
                if not where_clauses:
                    print(f"No se pueden eliminar productos de {table} (columnas incompatibles)")
                    continue
                
                # Parámetros para la consulta
                params = []
                for col in nombre_columns:
                    params.append(f"%{nombre}%")
                for col in codigo_columns:
                    params.append(f"%{codigo}%")
                
                # Eliminar registros
                query = f"DELETE FROM {table} WHERE {' OR '.join(where_clauses)}"
                cursor.execute(query, tuple(params))
                
                # Verificar cuántos registros se eliminaron
                if is_railway() or os.path.exists('railway.json'):
                    deleted_count = cursor.rowcount
                else:
                    deleted_count = conn.total_changes
                
                print(f"Eliminados {deleted_count} registros de '{nombre}' ({codigo}) en tabla {table}")
                
                if deleted_count > 0:
                    eliminados.append({
                        "tabla": table,
                        "producto": nombre,
                        "codigo": codigo,
                        "eliminados": deleted_count
                    })
        
        # Confirmar los cambios
        conn.commit()
        
        return eliminados
    
    except Exception as e:
        print(f"Error eliminando productos: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def run_diagnostics(clean_products=False):
    """Ejecuta el diagnóstico completo"""
    print("="*80)
    print("DIAGNÓSTICO DE PRODUCTOS PERSISTENTES")
    print("="*80)
    print(f"Fecha y hora: {datetime.now()}")
    print(f"Entorno: {'Railway (PostgreSQL)' if is_railway() or os.path.exists('railway.json') else 'Local (SQLite)'}")
    print("="*80)
    
    print("\n1. EXAMINANDO BASE DE DATOS...")
    db_results = check_db_tables()
    
    print("\n2. EXAMINANDO ARCHIVOS EXCEL...")
    excel_results = check_excel_files()
    
    print("\n3. ANALIZANDO FUNCIONES DE BÚSQUEDA...")
    search_info = check_search_functions()
    
    # Si se solicita limpieza y se encontraron productos, intentar eliminarlos
    eliminados = None
    if clean_products and (db_results or excel_results):
        print("\n4. ELIMINANDO PRODUCTOS PROBLEMÁTICOS...")
        eliminados = eliminar_productos_problema()
    
    print("\n"+"="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    if db_results:
        print(f"\n✅ Se encontraron {len(db_results)} coincidencias en la base de datos:")
        for i, result in enumerate(db_results, 1):
            print(f"  {i}. Producto '{result['producto']}' ({result['codigo']}) en tabla {result['tabla']}")
    else:
        print("\n❌ No se encontraron coincidencias en la base de datos.")
    
    if excel_results:
        print(f"\n✅ Se encontraron {len(excel_results)} coincidencias en archivos Excel:")
        for i, result in enumerate(excel_results, 1):
            archivo = os.path.basename(result['archivo'])
            print(f"  {i}. Producto '{result['producto']}' ({result['codigo']}) en archivo {archivo}")
    else:
        print("\n❌ No se encontraron coincidencias en archivos Excel.")
    
    if eliminados:
        print(f"\n✅ Se eliminaron productos de {len(eliminados)} ubicaciones:")
        for i, result in enumerate(eliminados, 1):
            print(f"  {i}. Producto '{result['producto']}' ({result['codigo']}): {result['eliminados']} registros eliminados de tabla {result['tabla']}")
    
    print("\n"+"="*80)
    print("CONCLUSIÓN")
    print("="*80)
    
    if not db_results and not excel_results:
        print("No se encontraron los productos problemáticos en ninguna fuente examinada.")
        print("Posibles causas:")
        print("1. Los productos podrían estar en archivos no examinados")
        print("2. Podría haber un caché en la aplicación")
        print("3. La búsqueda podría estar utilizando otra fuente de datos")
        print("4. Revisar las funciones de búsqueda para entender cómo se obtienen los productos")
    elif db_results:
        print("Los productos problemáticos SIGUEN PRESENTES en la base de datos.")
        print("Acción recomendada: Ejecutar nuevamente la limpieza de la base de datos")
        if clean_products and eliminados:
            print("Se ha intentado eliminar los productos problemáticos. Verificar si persisten.")
    elif excel_results:
        print("Los productos problemáticos están presentes en archivos Excel.")
        print("Acción recomendada: Revisar cómo la aplicación está leyendo estos archivos")
    
    # Guardar resultados en un archivo JSON
    try:
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "entorno": "Railway (PostgreSQL)" if is_railway() or os.path.exists('railway.json') else "Local (SQLite)",
            "resultados_db": db_results,
            "resultados_excel": excel_results,
            "analisis_busqueda": search_info,
            "productos_eliminados": eliminados
        }
        
        with open('diagnostico_productos_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=4, default=str)
        
        print("\nResultados detallados guardados en 'diagnostico_productos_resultado.json'")
    except Exception as e:
        print(f"Error al guardar resultados: {e}")
    
    print("\n"+"="*80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnóstico de productos persistentes')
    parser.add_argument('--clean', action='store_true', help='Eliminar productos problemáticos encontrados')
    
    args = parser.parse_args()
    
    run_diagnostics(clean_products=args.clean)