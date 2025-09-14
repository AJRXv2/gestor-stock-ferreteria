-- 003_add_indexes.sql
-- Índices para acelerar búsquedas frecuentes por codigo / proveedor / dueno.
-- Idempotente: utiliza IF NOT EXISTS (PostgreSQL) y comprobaciones manuales en SQLite.
-- Para SQLite: al no soportar CREATE INDEX IF NOT EXISTS en versiones antiguas, se intenta crear y se ignora error.

-- NOTA IMPORTANTE: Esta migración depende de que la columna dueno exista en productos_manual.
-- Si falla en PostgreSQL, ejecutar manualmente: ALTER TABLE productos_manual ADD COLUMN dueno TEXT;
-- En SQLite esto lo maneja ensure_productos_manual_columns() que corre automáticamente en init.

-- PostgreSQL: Esta sentencia solo se ejecutará en PostgreSQL
SELECT 'Verificando columna dueno en productos_manual para PostgreSQL';
-- PostgreSQL: Agregar columna dueno a productos_manual si no existe
-- SQLite ignorará esta sentencia gracias a adapt_sql_for_sqlite
ALTER TABLE productos_manual ADD COLUMN IF NOT EXISTS dueno TEXT;

-- STOCK: índice simple por codigo (para búsquedas directas)
CREATE INDEX IF NOT EXISTS idx_stock_codigo ON stock(LOWER(codigo));

-- STOCK: índice compuesto por proveedor + codigo (filtrado por proveedor y sincronización)
CREATE INDEX IF NOT EXISTS idx_stock_proveedor_codigo ON stock(LOWER(proveedor), LOWER(codigo));

-- STOCK: índice por dueno (filtrados frecuentes)
CREATE INDEX IF NOT EXISTS idx_stock_dueno ON stock(LOWER(dueno));

-- PRODUCTOS_MANUAL: índice por codigo
CREATE INDEX IF NOT EXISTS idx_prodmanual_codigo ON productos_manual(LOWER(codigo));

-- PRODUCTOS_MANUAL: índice por dueno
-- NOTA: Si la columna dueno no existe, este índice fallará.
-- Este índice fallará en Railway porque el esquema no tiene la columna dueno en productos_manual.
CREATE INDEX IF NOT EXISTS idx_prodmanual_dueno ON productos_manual(LOWER(dueno));

-- Nota: Si estás en SQLite y alguna sentencia falla por existir ya, es seguro.
