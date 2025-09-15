"""
Script para solucionar el problema de visibilidad de proveedores en Railway (PostgreSQL).

Este script aborda el problema de que cuando se agrega un proveedor a la ferretería,
no aparece en la sección de agregar productos ni en el área de gestionar productos
en la versión online.

El problema es específico de la versión online con PostgreSQL, donde las tablas
pueden tener restricciones diferentes a la versión local con SQLite.

Ejecución:
    python fix_railway_proveedores_visibilidad.py

Autor: GitHub Copilot
Fecha: 14/09/2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import DictCursor
import sqlite3
import json

# Configuración para detectar automáticamente el entorno
def is_railway_environment():
    """Detecta si el código se está ejecutando en Railway"""
    return os.environ.get('RAILWAY_ENVIRONMENT') is not None

def get_db_connection():
    """Obtiene una conexión a la base de datos (PostgreSQL en Railway, SQLite en local)"""
    if is_railway_environment() or os.environ.get('DATABASE_URL'):
        # Usar PostgreSQL en Railway
        db_url = os.environ.get('DATABASE_URL')
        try:
            conn = psycopg2.connect(db_url)
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"Error de conexión a PostgreSQL: {e}")
            return None
    else:
        # Usar SQLite en local
        database_file = 'gestor_stock.db'
        try:
            conn = sqlite3.connect(database_file)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Error de conexión a SQLite: {e}")
            return None

def execute_query(conn, query, params=(), fetch=False):
    """Ejecuta una consulta SQL con parámetros opcionales"""
    is_postgres = isinstance(conn, psycopg2.extensions.connection)
    
    # Adaptar la consulta según el motor de base de datos
    if is_postgres:
        # Reemplazar INSERT OR IGNORE por INSERT + ON CONFLICT DO NOTHING
        if "INSERT OR IGNORE INTO" in query:
            query = query.replace("INSERT OR IGNORE INTO", "INSERT INTO")
            if "ON CONFLICT" not in query:
                query = f"{query} ON CONFLICT DO NOTHING"
        
        # Reemplazar placeholders ? por %s para PostgreSQL
        if "?" in query and "%s" not in query:
            parts = []
            in_str = False
            for ch in query:
                if ch == "'":
                    in_str = not in_str
                    parts.append(ch)
                elif ch == '?' and not in_str:
                    parts.append('%s')
                else:
                    parts.append(ch)
            query = ''.join(parts)
    
    cursor = conn.cursor() if not is_postgres else conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            if is_postgres:
                result = [dict(row) for row in result]
            else:
                result = [dict(row) for row in result]
            return result
        else:
            if not is_postgres:
                conn.commit()
            return True
    except Exception as e:
        print(f"Error en la consulta: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        if not is_postgres:
            conn.rollback()
        return False
    finally:
        cursor.close()

def diagnosticar_proveedores():
    """Diagnostica el estado de proveedores en la base de datos"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    
    try:
        # Verificar tablas relacionadas con proveedores
        tablas = [
            "proveedores_manual",
            "proveedores_duenos",
            "proveedores_meta",
            "proveedores_ocultos"
        ]
        
        is_postgres = isinstance(conn, psycopg2.extensions.connection)
        
        print("=== DIAGNÓSTICO DE TABLAS DE PROVEEDORES ===")
        for tabla in tablas:
            if is_postgres:
                exists_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
                """
            else:
                exists_query = """
                SELECT count(*) as count FROM sqlite_master 
                WHERE type='table' AND name=?;
                """
            
            resultado = execute_query(conn, exists_query, (tabla,), fetch=True)
            existe = resultado[0]['exists'] if is_postgres else resultado[0]['count'] > 0
            
            if existe:
                count_query = f"SELECT COUNT(*) as count FROM {tabla}"
                count_result = execute_query(conn, count_query, (), fetch=True)
                count = count_result[0]['count']
                print(f"✅ Tabla '{tabla}' existe con {count} registros")
            else:
                print(f"❌ Tabla '{tabla}' no existe")
        
        # Verificar relaciones entre proveedores_manual y proveedores_duenos
        print("\n=== VERIFICACIÓN DE RELACIONES ENTRE TABLAS ===")
        query_relaciones = """
        SELECT p.id, p.nombre, COUNT(pd.dueno) as num_duenos
        FROM proveedores_manual p
        LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
        GROUP BY p.id, p.nombre
        ORDER BY p.nombre
        """
        
        relaciones = execute_query(conn, query_relaciones, (), fetch=True)
        print(f"Encontrados {len(relaciones)} proveedores:")
        
        for r in relaciones:
            print(f"- {r['nombre']} (ID: {r['id']}): {r['num_duenos']} dueño(s) asociado(s)")
        
        # Verificar proveedores sin dueños
        sin_dueno = [r for r in relaciones if r['num_duenos'] == 0]
        if sin_dueno:
            print(f"\n⚠️ Hay {len(sin_dueno)} proveedores sin dueños asociados:")
            for p in sin_dueno:
                print(f"  - {p['nombre']} (ID: {p['id']})")
        else:
            print("\n✅ Todos los proveedores tienen al menos un dueño asociado")
            
        # Verificar dueños existentes
        duenos_query = """
        SELECT DISTINCT dueno FROM proveedores_duenos
        """
        
        duenos = execute_query(conn, duenos_query, (), fetch=True)
        print(f"\nDueños existentes: {', '.join([d['dueno'] for d in duenos])}")
        
        return {
            "proveedores": relaciones,
            "sin_dueno": sin_dueno,
            "duenos": [d['dueno'] for d in duenos]
        }
        
    except Exception as e:
        print(f"Error durante el diagnóstico: {e}")
    finally:
        conn.close()

def corregir_proveedores_sin_dueno():
    """Corrige los proveedores que no tienen dueños asociados"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    
    try:
        # Primero diagnosticar para identificar proveedores sin dueño
        diagnostico = diagnosticar_proveedores()
        
        if not diagnostico or 'sin_dueno' not in diagnostico:
            print("No se pudo obtener diagnóstico")
            return
        
        if not diagnostico['sin_dueno']:
            print("No hay proveedores sin dueño que corregir")
            return
        
        # Por cada proveedor sin dueño, asociarlo a ambos dueños (para máxima visibilidad)
        print("\n=== CORRIGIENDO PROVEEDORES SIN DUEÑO ===")
        
        is_postgres = isinstance(conn, psycopg2.extensions.connection)
        corregidos = 0
        
        for p in diagnostico['sin_dueno']:
            proveedor_id = p['id']
            nombre = p['nombre']
            
            # Asociar a ambos dueños
            duenos = ['ricky', 'ferreteria_general']
            for d in duenos:
                if is_postgres:
                    query = """
                    INSERT INTO proveedores_duenos (proveedor_id, dueno)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """
                else:
                    query = """
                    INSERT OR IGNORE INTO proveedores_duenos (proveedor_id, dueno)
                    VALUES (?, ?)
                    """
                
                result = execute_query(conn, query, (proveedor_id, d), fetch=False)
                
                # También añadir a proveedores_meta (legacy)
                if is_postgres:
                    meta_query = """
                    INSERT INTO proveedores_meta (nombre, dueno)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """
                else:
                    meta_query = """
                    INSERT OR IGNORE INTO proveedores_meta (nombre, dueno)
                    VALUES (?, ?)
                    """
                
                execute_query(conn, meta_query, (nombre, d), fetch=False)
            
            print(f"✅ Proveedor '{nombre}' (ID: {proveedor_id}) asociado a ambos dueños")
            corregidos += 1
        
        print(f"\n✅ Corrección completada: {corregidos} proveedores asociados a dueños")
        
    except Exception as e:
        print(f"Error al corregir proveedores: {e}")
    finally:
        conn.close()

def verificar_indices_constraints():
    """Verifica y corrige índices y constraints en tablas de proveedores para PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    
    is_postgres = isinstance(conn, psycopg2.extensions.connection)
    if not is_postgres:
        print("Esta función solo es relevante para PostgreSQL")
        conn.close()
        return
    
    try:
        print("\n=== VERIFICANDO ÍNDICES Y CONSTRAINTS EN POSTGRESQL ===")
        
        # Verificar índices en proveedores_duenos
        indices_queries = [
            """
            CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_proveedor_id 
            ON proveedores_duenos(proveedor_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_proveedores_duenos_dueno 
            ON proveedores_duenos(dueno);
            """
        ]
        
        for query in indices_queries:
            execute_query(conn, query, (), fetch=False)
        
        print("✅ Índices verificados en proveedores_duenos")
        
        # Verificar constraint único en proveedores_duenos
        # Primero verificar si ya existe
        constraint_exists_query = """
        SELECT COUNT(*) as count FROM information_schema.table_constraints
        WHERE table_name = 'proveedores_duenos'
        AND constraint_name = 'proveedores_duenos_unique'
        AND constraint_type = 'UNIQUE';
        """
        
        constraint_exists = execute_query(conn, constraint_exists_query, (), fetch=True)
        
        if constraint_exists[0]['count'] == 0:
            # Crear constraint único
            constraint_query = """
            ALTER TABLE proveedores_duenos 
            ADD CONSTRAINT proveedores_duenos_unique 
            UNIQUE (proveedor_id, dueno);
            """
            
            execute_query(conn, constraint_query, (), fetch=False)
            print("✅ Constraint único creado en proveedores_duenos")
        else:
            print("✅ Constraint único ya existe en proveedores_duenos")
        
    except Exception as e:
        print(f"Error al verificar índices y constraints: {e}")
    finally:
        conn.close()

def main():
    """Función principal que ejecuta las correcciones"""
    print("=== CORRECCIÓN DE VISIBILIDAD DE PROVEEDORES EN RAILWAY ===")
    print("Este script soluciona el problema de que los proveedores no aparecen")
    print("en la sección de agregar productos ni en gestionar productos en Railway.")
    print("\nIniciando diagnóstico...")
    
    # Diagnosticar antes de corregir
    diagnosticar_proveedores()
    
    # Verificar índices y constraints en PostgreSQL
    verificar_indices_constraints()
    
    # Corregir proveedores sin dueño
    corregir_proveedores_sin_dueno()
    
    # Diagnosticar después de corregir para confirmar
    print("\n=== DIAGNÓSTICO FINAL ===")
    diagnostico_final = diagnosticar_proveedores()
    
    if diagnostico_final and 'sin_dueno' in diagnostico_final:
        if not diagnostico_final['sin_dueno']:
            print("\n✅ CORRECCIÓN EXITOSA: Todos los proveedores tienen dueños asociados")
        else:
            print(f"\n⚠️ Aún hay {len(diagnostico_final['sin_dueno'])} proveedores sin dueño")
    
    print("\nPara reflejar estos cambios en la aplicación, reinicie el servidor en Railway.")

if __name__ == "__main__":
    main()