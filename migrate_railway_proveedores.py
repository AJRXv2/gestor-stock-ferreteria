#!/usr/bin/env python3
"""
Script de migración Railway para corregir el problema de proveedores.

Este script:
1. Crea la tabla proveedores_duenos si no existe
2. Migra datos desde proveedores_meta
3. Sincroniza las tablas
4. Verifica que la corrección funciona

Uso:
- Ejecutar desde la aplicación web: /admin/proveedores
- O usar curl: curl -X POST https://tu-app.railway.app/api/sincronizar_proveedores
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_railway_environment():
    """Detecta si estamos ejecutándose en Railway"""
    return (
        os.environ.get('RAILWAY_ENVIRONMENT') is not None or
        os.environ.get('DATABASE_URL') is not None
    )

def migrate_railway_proveedores():
    """
    Ejecuta la migración completa para el problema de proveedores en Railway.
    """
    logger.info("🚀 Iniciando migración Railway para proveedores...")
    
    try:
        # Importar desde gestor solo si es necesario
        if 'gestor' not in sys.modules:
            try:
                from gestor import (
                    get_db_connection, 
                    _is_postgres_configured,
                    db_query
                )
            except ImportError as e:
                logger.error(f"❌ Error importando módulos: {e}")
                return False
        
        # Verificar que estamos en PostgreSQL
        if not _is_postgres_configured():
            logger.warning("⚠️ No se detectó configuración PostgreSQL. Saltando migración.")
            return True
        
        logger.info("✅ Entorno PostgreSQL detectado. Procediendo con migración...")
        
        # Paso 1: Crear tabla proveedores_duenos si no existe
        logger.info("📝 Paso 1: Creando tabla proveedores_duenos...")
        
        success = db_query("""
            CREATE TABLE IF NOT EXISTS proveedores_duenos (
                id SERIAL PRIMARY KEY,
                proveedor_id INTEGER NOT NULL,
                dueno TEXT NOT NULL,
                CONSTRAINT proveedores_duenos_unique UNIQUE (proveedor_id, dueno),
                CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE
            )
        """)
        
        if not success:
            logger.error("❌ Error creando tabla proveedores_duenos")
            return False
        
        logger.info("✅ Tabla proveedores_duenos creada/verificada")
        
        # Paso 2: Crear índices
        logger.info("📝 Paso 2: Creando índices...")
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno)"
        ]
        
        for indice in indices:
            db_query(indice)
        
        logger.info("✅ Índices creados")
        
        # Paso 3: Migrar datos desde proveedores_meta
        logger.info("📝 Paso 3: Migrando datos desde proveedores_meta...")
        
        migration_success = db_query("""
            INSERT INTO proveedores_duenos (proveedor_id, dueno)
            SELECT pm.id, meta.dueno 
            FROM proveedores_meta meta
            JOIN proveedores_manual pm ON pm.nombre = meta.nombre
            ON CONFLICT (proveedor_id, dueno) DO NOTHING
        """)
        
        if not migration_success:
            logger.error("❌ Error migrando datos desde proveedores_meta")
            return False
        
        logger.info("✅ Datos migrados desde proveedores_meta")
        
        # Paso 4: Verificar migración
        logger.info("📝 Paso 4: Verificando migración...")
        
        # Contar registros
        meta_count = db_query("SELECT COUNT(*) as count FROM proveedores_meta", fetch=True)
        duenos_count = db_query("SELECT COUNT(*) as count FROM proveedores_duenos", fetch=True)
        
        if meta_count and duenos_count:
            meta_total = meta_count[0]['count']
            duenos_total = duenos_count[0]['count']
            
            logger.info(f"📊 proveedores_meta: {meta_total} registros")
            logger.info(f"📊 proveedores_duenos: {duenos_total} registros")
            
            if duenos_total >= meta_total:
                logger.info("✅ Migración verificada correctamente")
            else:
                logger.warning(f"⚠️ Posible problema: proveedores_duenos tiene menos registros ({duenos_total}) que proveedores_meta ({meta_total})")
        
        # Paso 5: Verificar consulta del formulario
        logger.info("📝 Paso 5: Verificando consulta del formulario...")
        
        for dueno in ['ferreteria_general', 'ricky']:
            proveedores = db_query("""
                SELECT DISTINCT p.nombre 
                FROM proveedores_manual p
                JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
                WHERE pd.dueno = %s
                ORDER BY p.nombre
            """, (dueno,), fetch=True)
            
            if proveedores:
                nombres = [p['nombre'] for p in proveedores]
                logger.info(f"  ✅ {dueno}: {len(nombres)} proveedores ({', '.join(nombres)})")
            else:
                logger.warning(f"  ⚠️ {dueno}: No se encontraron proveedores")
        
        logger.info("🎉 ¡Migración completada exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Error durante migración: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def migrate_default_providers():
    """
    Asegura que los proveedores por defecto estén presentes con las relaciones correctas.
    """
    logger.info("📝 Asegurando proveedores por defecto...")
    
    try:
        from gestor import db_query
        
        # Proveedores por defecto con sus dueños
        default_providers = [
            # Ferretería General
            ("DECKER", "ferreteria_general"),
            ("JELUZ", "ferreteria_general"), 
            ("SICA", "ferreteria_general"),
            ("Otros Proveedores", "ferreteria_general"),
            
            # Ricky
            ("BremenTools", "ricky"),
            ("Berger", "ricky"),
            ("Cachan", "ricky"),
            ("Chiesa", "ricky"),
            ("Crossmaster", "ricky"),
            
            # MIG para ambos
            ("MIG", "ferreteria_general"),
            ("MIG", "ricky")
        ]
        
        for nombre, dueno in default_providers:
            # Asegurar que el proveedor existe
            db_query("INSERT INTO proveedores_manual (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", (nombre,))
            
            # Obtener ID del proveedor
            proveedor_data = db_query("SELECT id FROM proveedores_manual WHERE nombre = %s LIMIT 1", (nombre,), fetch=True)
            
            if proveedor_data:
                proveedor_id = proveedor_data[0]['id']
                
                # Asegurar relación en proveedores_duenos
                db_query("""
                    INSERT INTO proveedores_duenos (proveedor_id, dueno) 
                    VALUES (%s, %s) 
                    ON CONFLICT (proveedor_id, dueno) DO NOTHING
                """, (proveedor_id, dueno))
                
                # Asegurar relación en proveedores_meta para compatibilidad
                db_query("""
                    INSERT INTO proveedores_meta (nombre, dueno) 
                    VALUES (%s, %s) 
                    ON CONFLICT (nombre, dueno) DO NOTHING
                """, (nombre, dueno))
        
        logger.info("✅ Proveedores por defecto configurados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error configurando proveedores por defecto: {e}")
        return False

def main():
    """Función principal de migración"""
    logger.info("🔧 Iniciando migración Railway para problema de proveedores")
    
    if not is_railway_environment():
        logger.info("ℹ️ No se detectó entorno Railway. Ejecutando en modo local/desarrollo.")
    else:
        logger.info("🚂 Entorno Railway detectado. Ejecutando migración de producción.")
    
    # Ejecutar migración
    if migrate_railway_proveedores():
        logger.info("✅ Migración principal completada")
        
        # Configurar proveedores por defecto
        if migrate_default_providers():
            logger.info("✅ Configuración de proveedores por defecto completada")
            logger.info("🎉 ¡MIGRACIÓN COMPLETA!")
            logger.info("📝 Los proveedores ahora deberían aparecer correctamente en el formulario de agregar productos")
            return True
        else:
            logger.warning("⚠️ Migración principal exitosa, pero falló la configuración de proveedores por defecto")
            return False
    else:
        logger.error("❌ Migración principal falló")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)