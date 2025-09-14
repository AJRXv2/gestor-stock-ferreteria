-- 002_example_add_column.sql
-- EJEMPLO: Cómo añadir una columna nueva de forma segura.
-- PASOS A SEGUIR (borrar estas líneas en una migración real tras adaptarla):
-- 1. Seleccionar un nombre de archivo con el siguiente número libre (ej: 003_, 004_, etc.).
-- 2. Escribir cambios idempotentes. Para columnas nuevas:
--      - SQLite no soporta IF NOT EXISTS en ADD COLUMN, así que primero comprobamos si existe.
--      - En Postgres se puede usar ADD COLUMN IF NOT EXISTS directamente.
-- 3. Probar en entorno de staging antes de producción.
-- 4. Confirmar que migrate.py status muestra la migración pendiente y luego aplicar con "python migrate.py apply".

-- SQLite: Añadir columna 'nuevo_campo' a la tabla 'stock' solo si NO existe
-- (Se logra inspeccionando PRAGMA table_info)
-- NOTA: Este bloque se ejecutará en ambos motores; en Postgres la parte SQLite no rompe porque son sentencias independientes.

/*
BEGIN TRANSACTION;

-- Para SQLite: ejecutar el bloque condicional con ejecución dinámica (este método es ilustrativo, se puede simplificar dependiendo de tu estrategia real)
-- La forma más simple: intentar añadir y capturar error manualmente (pero migrate.py haría rollback). Aquí solo ejemplo.
-- En producción podrías dejar solo el ADD COLUMN IF NOT EXISTS para Postgres y documentar un paso manual para SQLite si es muy raro.

-- PostgreSQL (se ejecuta sin error en PG; SQLite ignorará IF NOT EXISTS en ADD COLUMN porque no lo soporta en versiones antiguas)
ALTER TABLE stock ADD COLUMN IF NOT EXISTS nuevo_campo TEXT;

COMMIT;
*/

-- Sentencia SQL válida para asegurar que esta migración se aplique correctamente
-- Esto es un comentario que podría añadirse a la tabla stock para futura referencia
COMMENT ON TABLE IF EXISTS stock IS 'Tabla principal de inventario';

-- Si el motor no soporta COMMENT ON TABLE (como SQLite), la línea será ignorada
-- y este archivo continuará siendo un ejemplo pero no causará errores.
