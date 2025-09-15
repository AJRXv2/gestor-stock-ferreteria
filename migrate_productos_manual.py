"""
Script para migrar productos desde productos_manual.xlsx a la tabla productos_manual en la base de datos.
Asegura que la tabla productos_manual tenga todos los campos necesarios y migra los datos existentes.
"""

import os
import pandas as pd
import sqlite3
import psycopg2
import psycopg2.extras
import json
from datetime import datetime

# Constantes
EXCEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listas_excel')
MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, 'productos_manual.xlsx')
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gestor_stock.db')

def is_railway():
    """Determina si estamos en Railway verificando las variables de entorno"""
    return bool(os.environ.get('RAILWAY_ENVIRONMENT', False))

def get_db_connection():
    """Establece una conexión a la base de datos según el entorno"""
    if is_railway():
        # Usar credenciales de Railway
        try:
            railway_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'railway.json')
            with open(railway_json, 'r') as f:
                railway_config = json.load(f)
            
            postgres_url = railway_config.get('POSTGRES_URL', '')
            if not postgres_url:
                raise ValueError("POSTGRES_URL no encontrado en railway.json")
            
            conn = psycopg2.connect(postgres_url)
            conn.cursor_factory = psycopg2.extras.DictCursor
            return conn
        except Exception as e:
            print(f"Error conectando a PostgreSQL: {e}")
            return None
    else:
        # Usar SQLite
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Error conectando a SQLite: {e}")
            return None

def ensure_table_structure():
    """Asegura que la tabla productos_manual tenga todos los campos necesarios"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return False

    try:
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        if is_railway():
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'productos_manual'
                );
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='productos_manual';
            """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists or (is_railway() and not table_exists[0]) or (not is_railway() and not table_exists):
            # La tabla no existe, crearla
            if is_railway():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS productos_manual (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        codigo TEXT,
                        precio REAL DEFAULT 0,
                        proveedor TEXT,
                        observaciones TEXT,
                        dueno TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS productos_manual (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        codigo TEXT,
                        precio REAL DEFAULT 0,
                        proveedor TEXT,
                        observaciones TEXT,
                        dueno TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            print("Tabla productos_manual creada")
        else:
            # Verificar la estructura de la tabla
            if is_railway():
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'productos_manual';
                """)
            else:
                cursor.execute("PRAGMA table_info(productos_manual);")
            
            columns = cursor.fetchall()
            column_names = [col['column_name'] if is_railway() else col['name'] for col in columns]
            
            required_columns = ['nombre', 'codigo', 'precio', 'proveedor', 'observaciones', 'dueno']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            # Agregar columnas faltantes
            for col in missing_columns:
                if is_railway():
                    cursor.execute(f"ALTER TABLE productos_manual ADD COLUMN {col} TEXT;")
                else:
                    cursor.execute(f"ALTER TABLE productos_manual ADD COLUMN {col} TEXT;")
                print(f"Columna {col} agregada a la tabla productos_manual")
        
        conn.commit()
        print("Estructura de tabla verificada y actualizada si fue necesario")
        return True
    except Exception as e:
        print(f"Error verificando/actualizando la estructura de la tabla: {e}")
        return False
    finally:
        conn.close()

def get_excel_data():
    """Lee los datos del Excel productos_manual.xlsx"""
    if not os.path.exists(MANUAL_PRODUCTS_FILE):
        print(f"Archivo no encontrado: {MANUAL_PRODUCTS_FILE}")
        return None
    
    try:
        print(f"Leyendo archivo Excel: {MANUAL_PRODUCTS_FILE}")
        df = pd.read_excel(MANUAL_PRODUCTS_FILE)
        
        # Renombrar columnas si es necesario
        if 'Código' in df.columns and 'Codigo' not in df.columns:
            df.rename(columns={'Código': 'Codigo'}, inplace=True)
        if 'Dueño' in df.columns and 'Dueno' not in df.columns:
            df.rename(columns={'Dueño': 'Dueno'}, inplace=True)
        
        print(f"Datos leídos del Excel: {len(df)} filas")
        return df
    except Exception as e:
        print(f"Error leyendo el archivo Excel: {e}")
        return None

def migrate_data(df):
    """Migra los datos del DataFrame a la tabla productos_manual"""
    if df is None or df.empty:
        print("No hay datos para migrar")
        return False
    
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Limpiar la tabla para evitar duplicados
        cursor.execute("DELETE FROM productos_manual")
        print("Tabla productos_manual limpiada")
        
        # Insertar datos
        count = 0
        for _, row in df.iterrows():
            # Extraer valores, manejar valores faltantes
            nombre = str(row.get('Nombre', '')) if pd.notna(row.get('Nombre', '')) else ''
            codigo = str(row.get('Codigo', '')) if pd.notna(row.get('Codigo', '')) else ''
            
            # Convertir precio a float, manejar formatos como strings
            precio_raw = row.get('Precio', 0)
            if pd.isna(precio_raw):
                precio = 0.0
            else:
                try:
                    # Intentar convertir a float, manejar formatos de texto
                    precio_str = str(precio_raw).replace('$', '').replace(',', '').strip()
                    precio = float(precio_str) if precio_str else 0.0
                except:
                    precio = 0.0
            
            proveedor = str(row.get('Proveedor', '')) if pd.notna(row.get('Proveedor', '')) else ''
            observaciones = str(row.get('Observaciones', '')) if pd.notna(row.get('Observaciones', '')) else ''
            dueno = str(row.get('Dueno', '')) if pd.notna(row.get('Dueno', '')) else ''
            
            # Insertar en la base de datos
            cursor.execute("""
                INSERT INTO productos_manual 
                (nombre, codigo, precio, proveedor, observaciones, dueno)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, codigo, precio, proveedor, observaciones, dueno))
            count += 1
        
        conn.commit()
        print(f"Migración completada: {count} productos insertados en la base de datos")
        return True
    except Exception as e:
        print(f"Error migrando los datos: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def backup_excel():
    """Hace una copia de seguridad del archivo Excel"""
    if not os.path.exists(MANUAL_PRODUCTS_FILE):
        print(f"Archivo no encontrado: {MANUAL_PRODUCTS_FILE}")
        return False
    
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"productos_manual_{timestamp}.xlsx")
        
        import shutil
        shutil.copy2(MANUAL_PRODUCTS_FILE, backup_file)
        print(f"Copia de seguridad creada: {backup_file}")
        return True
    except Exception as e:
        print(f"Error creando copia de seguridad: {e}")
        return False

def export_db_to_excel():
    """Exporta los datos de la tabla productos_manual de vuelta al Excel"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return False
    
    try:
        # Leer datos de la base de datos
        if is_railway():
            query = "SELECT nombre as Nombre, codigo as Codigo, precio as Precio, proveedor as Proveedor, observaciones as Observaciones, dueno as Dueno FROM productos_manual"
        else:
            query = "SELECT nombre as Nombre, codigo as Codigo, precio as Precio, proveedor as Proveedor, observaciones as Observaciones, dueno as Dueno FROM productos_manual"
        
        df = pd.read_sql_query(query, conn)
        
        # Renombrar columnas para mantener formato original
        if 'Codigo' in df.columns and 'Código' not in df.columns:
            df.rename(columns={'Codigo': 'Código'}, inplace=True)
        if 'Dueno' in df.columns and 'Dueño' not in df.columns:
            df.rename(columns={'Dueno': 'Dueño'}, inplace=True)
        
        # Guardar en Excel
        df.to_excel(MANUAL_PRODUCTS_FILE, index=False)
        print(f"Datos exportados al Excel: {MANUAL_PRODUCTS_FILE}")
        return True
    except Exception as e:
        print(f"Error exportando datos al Excel: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("==== MIGRACIÓN DE PRODUCTOS MANUALES ====")
    
    # Hacer backup del Excel
    print("\n1. Realizando copia de seguridad del Excel...")
    if backup_excel():
        print("✅ Copia de seguridad completada")
    else:
        print("❌ No se pudo crear la copia de seguridad. Abortando migración.")
        exit(1)
    
    # Verificar estructura de la tabla
    print("\n2. Verificando estructura de la tabla en la base de datos...")
    if ensure_table_structure():
        print("✅ Estructura de tabla verificada")
    else:
        print("❌ Error verificando la estructura de tabla. Abortando migración.")
        exit(1)
    
    # Leer datos del Excel
    print("\n3. Leyendo datos del archivo Excel...")
    df = get_excel_data()
    if df is not None:
        print(f"✅ Datos leídos: {len(df)} productos")
    else:
        print("❌ Error leyendo datos del Excel. Abortando migración.")
        exit(1)
    
    # Migrar datos
    print("\n4. Migrando datos a la base de datos...")
    if migrate_data(df):
        print("✅ Datos migrados correctamente")
    else:
        print("❌ Error migrando los datos. Abortando migración.")
        exit(1)
    
    # Exportar datos de vuelta al Excel (para verificar consistencia)
    print("\n5. Exportando datos de la base de datos al Excel (para verificación)...")
    if export_db_to_excel():
        print("✅ Exportación completada")
    else:
        print("⚠️ Advertencia: No se pudo exportar los datos de vuelta al Excel")
    
    print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("Los productos manuales ahora están disponibles en la base de datos.")
    print("El archivo Excel ha sido actualizado como respaldo.")