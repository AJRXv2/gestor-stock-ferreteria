-- Script de migracion para Railway PostgreSQL
-- Ejecutar este script para resolver problemas de esquema

-- 1. Tabla proveedores_duenos
CREATE TABLE IF NOT EXISTS proveedores_duenos (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL,
    dueno TEXT NOT NULL,
    CONSTRAINT proveedores_duenos_unique UNIQUE (proveedor_id, dueno),
    CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno);

-- 2. Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Verificar columna dueno en productos_manual
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

-- 4. Tabla de metadatos
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

-- 5. Correcciones a la tabla productos_manual
-- Eliminar duplicados (mantener el id mas bajo)
DELETE FROM productos_manual a
USING productos_manual b
WHERE a.id > b.id 
AND a.codigo = b.codigo
AND a.proveedor = b.proveedor
AND a.dueno = b.dueno;

-- 6. Verificar indices
CREATE INDEX IF NOT EXISTS idx_prodmanual_codigo ON productos_manual(codigo);
CREATE INDEX IF NOT EXISTS idx_prodmanual_proveedor ON productos_manual(proveedor);
CREATE INDEX IF NOT EXISTS idx_prodmanual_descripcion ON productos_manual(descripcion);

-- 7. Correcciones a la tabla proveedores_manual
-- Asegurar unicidad de nombres
ALTER TABLE proveedores_manual ADD CONSTRAINT IF NOT EXISTS proveedores_manual_nombre_unique UNIQUE (nombre);

-- Fin del script
SELECT 'Migracion completada con exito' as resultado;