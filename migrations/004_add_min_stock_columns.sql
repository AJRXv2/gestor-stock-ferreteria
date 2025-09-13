-- 004_add_min_stock_columns.sql
-- Añade columnas para avisos de stock bajo si no existen.
-- Columnas ya referenciadas en el código: avisar_bajo_stock (INTEGER) y min_stock_aviso (INTEGER / threshold)
-- Idempotente: usa ALTER TABLE ADD COLUMN IF NOT EXISTS en PostgreSQL. En SQLite se intentará añadir y si ya existe fallará silenciosamente en migrate.py (rollback). Si ya existen, se debe marcar manualmente.

-- PostgreSQL
ALTER TABLE stock ADD COLUMN IF NOT EXISTS avisar_bajo_stock INTEGER DEFAULT 0;
ALTER TABLE stock ADD COLUMN IF NOT EXISTS min_stock_aviso INTEGER;

-- NOTA: En SQLite (sin IF NOT EXISTS) esto puede fallar si las columnas ya existen.
-- Si tu base SQLite ya tiene estas columnas porque fueron añadidas por lógica anterior de init, simplemente marca esta migración como aplicada:
--   python migrate.py mark_all   (o aplica sólo hasta la 003 y luego marca la 004 si corresponde)
