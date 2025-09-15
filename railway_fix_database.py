#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir la base de datos en Railway PostgreSQL.
Este script resuelve problemas de estructura en la base de datos.
"""

import os
import psycopg2

def execute_migration():
    """Ejecuta la migracion en la base de datos PostgreSQL de Railway"""
    # Obtener la URL de la base de datos desde las variables de entorno
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        print("[ERROR] No se encontro la variable de entorno DATABASE_URL")
        return False
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # SQL para crear la tabla proveedores_duenos
        sql_proveedores_duenos = """
CREATE TABLE IF NOT EXISTS proveedores_duenos (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL,
    dueno TEXT NOT NULL,
    CONSTRAINT proveedores_duenos_unique UNIQUE (proveedor_id, dueno),
    CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno);
"""
        
        # Ejecutar script para crear tabla proveedores_duenos
        print("Creando tabla proveedores_duenos...")
        cur.execute(sql_proveedores_duenos)
        conn.commit()
        
        # SQL para corregir la tabla usuarios
        sql_usuarios = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        # Ejecutar script para tabla usuarios
        print("Verificando tabla usuarios...")
        cur.execute(sql_usuarios)
        conn.commit()
        
        # SQL para verificar tabla productos_manual
        sql_productos_manual = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'productos_manual' AND column_name = 'dueno'
    ) THEN
        ALTER TABLE productos_manual ADD COLUMN dueno TEXT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_prodmanual_dueno ON productos_manual(dueno);
"""
        
        # Ejecutar script para verificar productos_manual
        print("Verificando tabla productos_manual...")
        cur.execute(sql_productos_manual)
        conn.commit()
        
        # SQL para verificar tablas de metadatos
        sql_proveedores_meta = """
CREATE TABLE IF NOT EXISTS proveedores_meta (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    dueno TEXT,
    ruta_excel TEXT,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT proveedores_meta_unique UNIQUE (nombre, dueno)
);

CREATE INDEX IF NOT EXISTS idx_proveedores_meta_nombre ON proveedores_meta(nombre);
CREATE INDEX IF NOT EXISTS idx_proveedores_meta_dueno ON proveedores_meta(dueno);
"""
        
        # Ejecutar script para verificar proveedores_meta
        print("Verificando tabla proveedores_meta...")
        cur.execute(sql_proveedores_meta)
        conn.commit()
        
        print("[SUCCESS] Migracion aplicada correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error al aplicar la migracion: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("Iniciando migracion de base de datos en Railway...")
    result = execute_migration()
    print(f"Proceso finalizado con {'exito' if result else 'errores'}")