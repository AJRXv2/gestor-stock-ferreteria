"""
Función para verificar si el producto TERM32A existe en la base de datos.
Este es un script independiente para diagnóstico.
"""

import sqlite3
import psycopg2
import os

def _is_postgres_configured():
    """Determinar si estamos usando PostgreSQL (Railway) o SQLite (local)"""
    postgres_url = os.environ.get('DATABASE_URL', None)
    return postgres_url is not None

def conectar_bd():
    """Conectar a la base de datos según configuración"""
    if _is_postgres_configured():
        postgres_url = os.environ.get('DATABASE_URL', '')
        print(f"Conectando a PostgreSQL: {postgres_url}")
        conn = psycopg2.connect(postgres_url, sslmode='require')
    else:
        print("Conectando a SQLite local")
        conn = sqlite3.connect('gestor_stock.db')
        conn.row_factory = sqlite3.Row
    return conn

def buscar_term32a():
    """Buscar productos con código TERM32A en la base de datos"""
    conn = conectar_bd()
    cur = conn.cursor()
    
    print("===== BÚSQUEDA EN TABLA STOCK =====")
    try:
        cur.execute("SELECT * FROM stock WHERE codigo LIKE '%TERM32%' OR nombre LIKE '%TERM32%'")
        resultados = cur.fetchall()
        print(f"Resultados en tabla stock: {len(resultados)}")
        for r in resultados:
            print(r)
    except Exception as e:
        print(f"Error al buscar en stock: {e}")
    
    print("\n===== BÚSQUEDA EN TABLA PROVEEDORES_MANUAL =====")
    try:
        cur.execute("SELECT * FROM proveedores_manual WHERE nombre LIKE '%JELUZ%'")
        resultados = cur.fetchall()
        print(f"Resultados de proveedores JELUZ: {len(resultados)}")
        for r in resultados:
            print(r)
    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
    
    print("\n===== VERIFICAR TABLAS DISPONIBLES =====")
    try:
        if _is_postgres_configured():
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        else:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        tablas = cur.fetchall()
        print(f"Tablas disponibles: {len(tablas)}")
        for t in tablas:
            print(t)
    except Exception as e:
        print(f"Error al listar tablas: {e}")
    
    print("\n===== VERIFICAR RELACIONES PROVEEDOR-DUEÑO =====")
    try:
        cur.execute("""
            SELECT p.id, p.nombre, pd.dueno_id 
            FROM proveedores_manual p
            LEFT JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
            WHERE p.nombre LIKE '%JELUZ%'
        """)
        relaciones = cur.fetchall()
        print(f"Relaciones JELUZ-dueño: {len(relaciones)}")
        for r in relaciones:
            print(r)
    except Exception as e:
        print(f"Error al verificar relaciones: {e}")
    
    conn.close()
    print("\n===== FIN DIAGNÓSTICO BD =====")

if __name__ == "__main__":
    buscar_term32a()