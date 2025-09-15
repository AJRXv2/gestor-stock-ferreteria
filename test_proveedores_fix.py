#!/usr/bin/env python3
"""
Script de prueba para verificar la corrección del problema de proveedores
en el Gestor de Stock.

Este script:
1. Inicializa la base de datos con las nuevas correcciones
2. Verifica que la tabla proveedores_duenos se crea correctamente
3. Testea la sincronización entre tablas
4. Simula la consulta que usa el formulario de agregar productos
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import (
        init_db, 
        sincronizar_proveedores_meta_duenos, 
        db_query, 
        get_db_connection,
        _is_postgres_configured
    )
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    sys.exit(1)

def test_database_setup():
    """Testea la configuración inicial de la base de datos"""
    print("\n🔧 Paso 1: Inicializando base de datos...")
    
    try:
        init_db()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar BD: {e}")
        return False
    
    return True

def test_table_creation():
    """Verifica que todas las tablas necesarias existen"""
    print("\n🔧 Paso 2: Verificando creación de tablas...")
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Lista de tablas requeridas
        required_tables = [
            'proveedores_manual',
            'proveedores_meta', 
            'proveedores_duenos'
        ]
        
        use_postgres = _is_postgres_configured()
        
        for table in required_tables:
            try:
                if use_postgres:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        )
                    """, (table,))
                else:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """, (table,))
                
                result = cursor.fetchone()
                exists = result[0] if result else False
                
                if exists:
                    print(f"  ✅ Tabla '{table}' existe")
                else:
                    print(f"  ❌ Tabla '{table}' NO existe")
                    cursor.close()
                    conn.close()
                    return False
                    
            except Exception as e:
                print(f"  ❌ Error verificando tabla '{table}': {e}")
                cursor.close()
                conn.close()
                return False
        
        cursor.close()
        conn.close()
        print("✅ Todas las tablas requeridas existen")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def test_sample_data():
    """Inserta datos de prueba y verifica sincronización"""
    print("\n🔧 Paso 3: Insertando datos de prueba...")
    
    # Datos de prueba
    test_providers = [
        ("DECKER", "ferreteria_general"),
        ("JELUZ", "ferreteria_general"),
        ("MIG", "ferreteria_general"),
        ("SICA", "ferreteria_general"),
        ("Otros Proveedores", "ferreteria_general"),
        ("BremenTools", "ricky"),
        ("Berger", "ricky"),
        ("Cachan", "ricky"),
        ("Chiesa", "ricky"),
        ("Crossmaster", "ricky"),
        ("MIG", "ricky")  # MIG para ambos dueños
    ]
    
    try:
        for nombre, dueno in test_providers:
            # Insertar en proveedores_manual si no existe
            result = db_query(
                "INSERT OR IGNORE INTO proveedores_manual (nombre) VALUES (?)", 
                (nombre,)
            )
            
            # Obtener ID del proveedor
            proveedor_data = db_query(
                "SELECT id FROM proveedores_manual WHERE nombre = ? LIMIT 1",
                (nombre,), fetch=True
            )
            
            if proveedor_data:
                proveedor_id = proveedor_data[0]['id']
                
                # Insertar relación en proveedores_duenos
                db_query(
                    "INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)",
                    (proveedor_id, dueno)
                )
                
                # Insertar en proveedores_meta para compatibilidad
                db_query(
                    "INSERT OR IGNORE INTO proveedores_meta (nombre, dueno) VALUES (?, ?)",
                    (nombre, dueno)
                )
        
        print("✅ Datos de prueba insertados")
        return True
        
    except Exception as e:
        print(f"❌ Error insertando datos de prueba: {e}")
        return False

def test_synchronization():
    """Testea la función de sincronización"""
    print("\n🔧 Paso 4: Testeando sincronización...")
    
    try:
        success, message = sincronizar_proveedores_meta_duenos()
        
        if success:
            print(f"✅ Sincronización exitosa: {message}")
            return True
        else:
            print(f"❌ Sincronización falló: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        return False

def test_form_query():
    """Testea la consulta que usa el formulario de agregar productos"""
    print("\n🔧 Paso 5: Testeando consulta del formulario...")
    
    dueños_test = ['ferreteria_general', 'ricky']
    
    for dueno in dueños_test:
        try:
            print(f"\n  Consultando proveedores para '{dueno}':")
            
            # Esta es la consulta que usa obtener_proveedores_por_dueno()
            proveedores = db_query(
                """
                SELECT DISTINCT p.nombre 
                FROM proveedores_manual p
                JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
                WHERE pd.dueno = ?
                ORDER BY p.nombre
                """, 
                (dueno,), fetch=True
            )
            
            if proveedores:
                nombres = [p['nombre'] for p in proveedores]
                print(f"    ✅ Encontrados {len(nombres)} proveedores: {', '.join(nombres)}")
            else:
                print(f"    ❌ No se encontraron proveedores para '{dueno}'")
                return False
                
        except Exception as e:
            print(f"    ❌ Error consultando proveedores para '{dueno}': {e}")
            return False
    
    print("✅ Consultas del formulario funcionan correctamente")
    return True

def test_diagnostics():
    """Testea la función de diagnóstico"""
    print("\n🔧 Paso 6: Testeando diagnóstico...")
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Contar registros en cada tabla
        cursor.execute("SELECT COUNT(*) FROM proveedores_manual")
        manual_count = cursor.fetchone()[0]
        print(f"  📊 proveedores_manual: {manual_count} registros")
        
        cursor.execute("SELECT COUNT(*) FROM proveedores_meta")
        meta_count = cursor.fetchone()[0]
        print(f"  📊 proveedores_meta: {meta_count} registros")
        
        cursor.execute("SELECT COUNT(*) FROM proveedores_duenos")
        duenos_count = cursor.fetchone()[0]
        print(f"  📊 proveedores_duenos: {duenos_count} registros")
        
        # Verificar distribución por dueño
        cursor.execute("SELECT dueno, COUNT(*) FROM proveedores_duenos GROUP BY dueno")
        distribucion = cursor.fetchall()
        
        print("  📊 Distribución por dueño:")
        for dueno, count in distribucion:
            print(f"    - {dueno}: {count} proveedores")
        
        cursor.close()
        conn.close()
        
        print("✅ Diagnóstico completado")
        return True
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return False

def main():
    """Función principal del test"""
    print("🚀 Iniciando pruebas del sistema de proveedores")
    print("=" * 60)
    
    tests = [
        test_database_setup,
        test_table_creation,
        test_sample_data,
        test_synchronization,
        test_form_query,
        test_diagnostics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"\n❌ Prueba falló: {test.__name__}")
        except Exception as e:
            print(f"\n💥 Error inesperado en {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo.")
        print("\n📝 Próximos pasos:")
        print("   1. Despliega la aplicación actualizada a Railway")
        print("   2. Ve a /admin/proveedores para ejecutar la sincronización")
        print("   3. Verifica que los proveedores aparezcan en el formulario")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores anteriores.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)