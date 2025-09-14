import os
import re
import sys

# Configuración para detectar automáticamente el entorno
def is_railway_environment():
    """Detecta si el código se está ejecutando en Railway"""
    return os.environ.get('RAILWAY_ENVIRONMENT') is not None

def create_proveedores_duenos_table():
    """Script para crear la tabla proveedores_duenos en PostgreSQL"""
    # Esquema para la tabla proveedores_duenos
    schema = """
CREATE TABLE IF NOT EXISTS proveedores_duenos (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL,
    dueno TEXT NOT NULL,
    CONSTRAINT proveedores_duenos_unique UNIQUE (proveedor_id, dueno),
    CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno);

-- Migrando datos existentes desde proveedores_manual si tiene columna dueno
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'proveedores_manual' AND column_name = 'dueno'
    ) THEN
        INSERT INTO proveedores_duenos (proveedor_id, dueno)
        SELECT id, dueno FROM proveedores_manual 
        WHERE dueno IS NOT NULL
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
"""
    return schema

def fix_autoincrement_syntax():
    """Corrige la sintaxis AUTOINCREMENT a SERIAL para PostgreSQL"""
    # Esquema corregido para la tabla usuarios
    schema = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
    return schema

def check_productos_manual_table():
    """Verifica y corrige la tabla productos_manual"""
    # Esquema para verificar/corregir la tabla productos_manual
    schema = """
-- Verificar si la columna dueno existe en la tabla productos_manual
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'productos_manual' AND column_name = 'dueno'
    ) THEN
        ALTER TABLE productos_manual ADD COLUMN dueno TEXT;
    END IF;
END $$;

-- Índice actualizado para productos_manual
CREATE INDEX IF NOT EXISTS idx_prodmanual_dueno ON productos_manual(dueno);
"""
    return schema

def check_meta_tables():
    """Verifica y crea las tablas de metadatos"""
    schema = """
-- Tabla para guardar relaciones entre proveedores y archivos Excel
CREATE TABLE IF NOT EXISTS proveedores_meta (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    dueno TEXT,
    ruta_excel TEXT,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT proveedores_meta_unique UNIQUE (nombre, dueno)
);

-- Índices para la tabla proveedores_meta
CREATE INDEX IF NOT EXISTS idx_proveedores_meta_nombre ON proveedores_meta(nombre);
CREATE INDEX IF NOT EXISTS idx_proveedores_meta_dueno ON proveedores_meta(dueno);
"""
    return schema

def generate_migration_script():
    """Genera el script completo de migración"""
    script = """
-- Script de migración para Railway PostgreSQL
-- Ejecutar este script para resolver problemas de esquema

-- 1. Tabla proveedores_duenos
{}

-- 2. Corregir sintaxis AUTOINCREMENT
{}

-- 3. Verificar tabla productos_manual
{}

-- 4. Verificar tablas de metadatos
{}

-- Finalización
SELECT 'Migración completada con éxito' as resultado;
""".format(
        create_proveedores_duenos_table(),
        fix_autoincrement_syntax(),
        check_productos_manual_table(),
        check_meta_tables()
    )
    
    return script

def main():
    # Generar el script de migración
    migration_script = generate_migration_script()
    
    # Guardarlo en un archivo
    with open('railway_fix_database.sql', 'w') as f:
        f.write(migration_script)
    
    print("[SUCCESS] Script de migración generado: railway_fix_database.sql")
    print("Para aplicar este script en Railway:")
    print("1. Accede a la consola SQL de tu base de datos en Railway")
    print("2. Copia y pega el contenido del archivo generado")
    print("3. Ejecuta el script para crear las tablas faltantes")
    
    # Generar también un script Python para ejecutarlo
    py_script = """import os
import psycopg2
from urllib.parse import urlparse

def execute_migration():
    # Obtener la URL de la base de datos desde las variables de entorno
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("[ERROR] No se encontró la variable de entorno DATABASE_URL")
        return False
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Leer el script SQL
        with open('railway_fix_database.sql', 'r') as f:
            sql_script = f.read()
        
        # Ejecutar el script
        cur.execute(sql_script)
        
        # Commit y cerrar
        conn.commit()
        cur.close()
        conn.close()
        
        print("[SUCCESS] Migración aplicada correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error al aplicar la migración: {e}")
        return False

if __name__ == "__main__":
    execute_migration()
"""
    
    with open('railway_fix_database.py', 'w') as f:
        f.write(py_script)
    
    print("\nTambién se ha generado un script Python para ejecutar la migración:")
    print("railway_fix_database.py")
    print("Puedes ejecutarlo en Railway con: python railway_fix_database.py")

if __name__ == "__main__":
    main()