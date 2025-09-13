-- 003_add_indexes.sql
-- Índices para acelerar búsquedas frecuentes por codigo / proveedor / dueno.
-- Idempotente: utiliza IF NOT EXISTS (PostgreSQL) y comprobaciones manuales en SQLite.
-- Para SQLite: al no soportar CREATE INDEX IF NOT EXISTS en versiones antiguas, se intenta crear y se ignora error.

-- STOCK: índice simple por codigo (para búsquedas directas)
CREATE INDEX IF NOT EXISTS idx_stock_codigo ON stock(LOWER(codigo));
-- STOCK: índice compuesto por proveedor + codigo (filtrado por proveedor y sincronización)
CREATE INDEX IF NOT EXISTS idx_stock_proveedor_codigo ON stock(LOWER(proveedor), LOWER(codigo));
-- STOCK: índice por dueno (filtrados frecuentes)
CREATE INDEX IF NOT EXISTS idx_stock_dueno ON stock(LOWER(dueno));

-- PRODUCTOS_MANUAL: índice por codigo
CREATE INDEX IF NOT EXISTS idx_prodmanual_codigo ON productos_manual(LOWER(codigo));
-- PRODUCTOS_MANUAL: índice por dueno
CREATE INDEX IF NOT EXISTS idx_prodmanual_dueno ON productos_manual(LOWER(dueno));

-- Nota: Si estás en SQLite y alguna sentencia falla por existir ya, es seguro.
