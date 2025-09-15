#!/usr/bin/env python3
"""
Script minimalista para Railway - Solo crear tabla proveedores_duenos

Este script únicamente:
1. Crea la tabla proveedores_duenos si no existe
2. NO migra datos existentes
3. Los proveedores nuevos que agregues manualmente funcionarán correctamente

Uso directo en Railway:
https://tu-app.railway.app/fix_railway_simple/railway_fix_2024
"""

import os
import sys

def crear_tabla_proveedores_duenos():
    """Crea únicamente la tabla proveedores_duenos sin migrar datos"""
    print("🔧 Creando tabla proveedores_duenos para Railway...")
    
    try:
        from gestor import db_query, _is_postgres_configured
        
        if not _is_postgres_configured():
            print("❌ No es PostgreSQL. Este script es solo para Railway.")
            return False
        
        print("✅ PostgreSQL detectado")
        
        # Solo crear la tabla, SIN migración de datos
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
        if not success:
            print("❌ Error creando tabla proveedores_duenos")
            return False
        
        print("✅ Tabla proveedores_duenos creada")
        
        # Crear índices básicos
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id ON proveedores_duenos(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno ON proveedores_duenos(dueno)"
        ]
        
        for indice in indices:
            db_query(indice)
        
        print("✅ Índices creados")
        
        # Verificar que la función _upsert_proveedor funcione
        print("🧪 Probando agregar proveedor de prueba...")
        
        # Agregar un proveedor de prueba
        test_result = db_query("INSERT INTO proveedores_manual (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", ("PROVEEDOR_TEST",))
        
        if test_result:
            # Obtener ID del proveedor de prueba
            proveedor_data = db_query("SELECT id FROM proveedores_manual WHERE nombre = %s LIMIT 1", ("PROVEEDOR_TEST",), fetch=True)
            
            if proveedor_data:
                proveedor_id = proveedor_data[0]['id']
                
                # Probar inserción en proveedores_duenos
                test_duenos = db_query("""
                    INSERT INTO proveedores_duenos (proveedor_id, dueno) 
                    VALUES (%s, %s) 
                    ON CONFLICT (proveedor_id, dueno) DO NOTHING
                """, (proveedor_id, "ferreteria_general"))
                
                if test_duenos:
                    print("✅ Prueba de inserción exitosa")
                    
                    # Probar consulta del formulario
                    proveedores = db_query("""
                        SELECT DISTINCT p.nombre 
                        FROM proveedores_manual p
                        JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
                        WHERE pd.dueno = %s
                        ORDER BY p.nombre
                    """, ("ferreteria_general",), fetch=True)
                    
                    if proveedores:
                        print("✅ Consulta del formulario funciona")
                    else:
                        print("⚠️ Consulta del formulario no devolvió resultados")
                    
                    # Limpiar proveedor de prueba
                    db_query("DELETE FROM proveedores_duenos WHERE proveedor_id = %s", (proveedor_id,))
                    db_query("DELETE FROM proveedores_manual WHERE nombre = %s", ("PROVEEDOR_TEST",))
                    print("🧹 Proveedor de prueba eliminado")
                    
                else:
                    print("❌ Error en prueba de inserción")
                    return False
            else:
                print("❌ No se pudo obtener ID del proveedor de prueba")
                return False
        else:
            print("❌ Error creando proveedor de prueba")
            return False
        
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print("📝 Ahora cuando agregues proveedores manualmente:")
        print("   1. Se guardarán en proveedores_manual")
        print("   2. Se asociarán automáticamente en proveedores_duenos")
        print("   3. Aparecerán en el formulario de agregar productos")
        print("   4. Funcionarán en los filtros de búsqueda")
        
        return True
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = crear_tabla_proveedores_duenos()
    sys.exit(0 if success else 1)