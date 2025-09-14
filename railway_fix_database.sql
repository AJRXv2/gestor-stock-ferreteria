
-- Script de migración para Railway PostgreSQL
-- Ejecutar este script para resolver problemas de esquema

-- 1. Tabla proveedores_duenos

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


-- 2. Corregir sintaxis AUTOINCREMENT

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 3. Verificar tabla productos_manual

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


-- 4. Verificar tablas de metadatos

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


-- Finalización
SELECT 'Migración completada con éxito' as resultado;
