#!/usr/bin/env python3
"""
Script de acceso directo para Railway - Corrección de Proveedores

Este script puede ejecutarse directamente en Railway para corregir
el problema de proveedores sin necesidad de interfaz web.

Uso:
python fix_railway_direct.py
"""

import os
import sys

def is_railway():
    """Detecta si estamos en Railway"""
    return os.environ.get('RAILWAY_ENVIRONMENT') is not None

def fix_proveedores_railway():
    """Corrección directa para Railway"""
    print("🚂 Corrección Railway - Problema de Proveedores")
    print("=" * 50)
    
    if not is_railway():
        print("⚠️ No se detectó entorno Railway. Continuando en modo local...")
    
    try:
        # Importar módulos necesarios
        print("📦 Importando módulos...")
        from gestor import (
            get_db_connection,
            _is_postgres_configured, 
            db_query,
            sincronizar_proveedores_meta_duenos
        )
        print("✅ Módulos importados")
        
        # Verificar PostgreSQL
        if not _is_postgres_configured():
            print("❌ PostgreSQL no configurado")
            return False
        
        print("✅ PostgreSQL detectado")
        
        # Paso 1: Crear tabla proveedores_duenos
        print("\n🔧 Paso 1: Creando tabla proveedores_duenos...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS proveedores_duenos (
            id SERIAL PRIMARY KEY,
            proveedor_id INTEGER NOT NULL,
            dueno TEXT NOT NULL,
            CONSTRAINT proveedores_duenos_unique UNIQUE (proveedor_id, dueno),
            CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE
        )
        """
        
        success = db_query(create_table_sql)
        if success:
            print("✅ Tabla proveedores_duenos creada/verificada")
        else:
            print("❌ Error creando tabla")
            return False
        
        # Paso 2: Crear índices
        print("\n🔧 Paso 2: Creando índices...")
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno)"
        ]
        
        for indice in indices:
            db_query(indice)
        
        print("✅ Índices creados")
        
        # Paso 3: Sincronización
        print("\n🔧 Paso 3: Ejecutando sincronización...")
        
        success, message = sincronizar_proveedores_meta_duenos()
        
        if success:
            print(f"✅ Sincronización exitosa: {message}")
        else:
            print(f"❌ Sincronización falló: {message}")
            return False
        
        # Paso 4: Agregar proveedores por defecto
        print("\n🔧 Paso 4: Configurando proveedores por defecto...")
        
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
            # Asegurar proveedor existe
            db_query("INSERT INTO proveedores_manual (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", (nombre,))
            
            # Obtener ID
            proveedor_data = db_query("SELECT id FROM proveedores_manual WHERE nombre = %s LIMIT 1", (nombre,), fetch=True)
            
            if proveedor_data:
                proveedor_id = proveedor_data[0]['id']
                
                # Agregar a proveedores_duenos
                db_query("""
                    INSERT INTO proveedores_duenos (proveedor_id, dueno) 
                    VALUES (%s, %s) 
                    ON CONFLICT (proveedor_id, dueno) DO NOTHING
                """, (proveedor_id, dueno))
                
                # Agregar a proveedores_meta
                db_query("""
                    INSERT INTO proveedores_meta (nombre, dueno) 
                    VALUES (%s, %s) 
                    ON CONFLICT (nombre, dueno) DO NOTHING
                """, (nombre, dueno))
        
        print("✅ Proveedores por defecto configurados")
        
        # Paso 5: Verificación final
        print("\n🔧 Paso 5: Verificación final...")
        
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
                print(f"  ✅ {dueno}: {len(nombres)} proveedores")
                for nombre in nombres:
                    print(f"    - {nombre}")
            else:
                print(f"  ❌ {dueno}: No se encontraron proveedores")
                return False
        
        print("\n🎉 ¡CORRECCIÓN COMPLETADA EXITOSAMENTE!")
        print("📝 Los proveedores ahora deberían aparecer en el formulario de agregar productos")
        return True
        
    except Exception as e:
        print(f"\n💥 Error durante la corrección: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_proveedores_railway()
    print(f"\n{'='*50}")
    if success:
        print("✅ Resultado: ÉXITO")
        sys.exit(0)
    else:
        print("❌ Resultado: FALLÓ")
        sys.exit(1)