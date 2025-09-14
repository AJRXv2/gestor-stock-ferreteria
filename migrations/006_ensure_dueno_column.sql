-- 006_ensure_dueno_column.sql
-- Asegura que la columna dueno exista en la tabla productos_manual
-- Esta es una migración de seguridad en caso de que la columna no se haya creado correctamente antes

-- PostgreSQL
ALTER TABLE productos_manual ADD COLUMN IF NOT EXISTS dueno TEXT;

-- Intenta recrear el índice si no existe
DROP INDEX IF EXISTS idx_prodmanual_dueno;
CREATE INDEX idx_prodmanual_dueno ON productos_manual(LOWER(dueno));

-- Nota: En SQLite se manejará por el sistema de adaptación de SQL