-- 001_baseline.sql
-- Esquema inicial consolidado. Solo debe ejecutarse una vez en entornos nuevos.
-- Usa CREATE TABLE IF NOT EXISTS para ser idempotente (no modifica tablas existentes).
-- IMPORTANTE: No elimina ni altera columnas ya existentes.

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT NOT NULL,
    precio REAL DEFAULT 0,
    cantidad INTEGER DEFAULT 0,
    fecha_compra TEXT,
    proveedor TEXT,
    observaciones TEXT,
    precio_texto TEXT,
    dueno TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER,
    codigo TEXT,
    nombre TEXT,
    precio REAL,
    cantidad INTEGER,
    fecha_compra TEXT,
    proveedor TEXT,
    observaciones TEXT,
    precio_texto TEXT,
    dueno TEXT,
    created_at TEXT,
    fecha_evento TEXT,
    tipo_cambio TEXT,
    fuente TEXT,
    usuario TEXT
);

CREATE TABLE IF NOT EXISTS carrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT,
    precio REAL,
    cantidad INTEGER,
    proveedor TEXT,
    observaciones TEXT,
    precio_texto TEXT,
    dueno TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS productos_manual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    codigo TEXT,
    precio REAL DEFAULT 0,
    proveedor TEXT,
    observaciones TEXT,
    dueno TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proveedores_manual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    oculto INTEGER DEFAULT 0,
    dueno TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proveedores_ocultos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dueno TEXT,
    ocultado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de control de migraciones
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
