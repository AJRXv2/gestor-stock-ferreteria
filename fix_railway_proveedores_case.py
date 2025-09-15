#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para normalizar los nombres de proveedores en la base de datos PostgreSQL
Este script normaliza los nombres de proveedores en la tabla productos_manual
para que coincidan exactamente con las claves en PROVEEDOR_CONFIG
"""

import os
import json
import sys
import traceback
import psycopg2
import psycopg2.extras

# Importar desde gestor.py
try:
    from gestor import PROVEEDOR_CONFIG, _is_postgres_configured
except ImportError:
    print("[ERROR] No se pudo importar desde gestor.py")
    sys.exit(1)

def normalizar_proveedores():
    """Normalizar nombres de proveedores en la tabla productos_manual"""
    if not _is_postgres_configured():
        print("[ERROR] Este script solo funciona en entorno PostgreSQL (Railway)")
        return False
    
    try:
        # Conectar a la base de datos
        dsn = os.environ.get('DATABASE_URL', '')
        if dsn.startswith('postgres://'):
            dsn = dsn.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(dsn)
        conn.set_session(autocommit=True)
        
        # Usar cursor de diccionario para obtener resultados con nombres de columnas
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 1. Obtener todos los proveedores únicos en la tabla
        cur.execute("""
            SELECT DISTINCT proveedor 
            FROM productos_manual 
            WHERE proveedor IS NOT NULL AND proveedor != ''
        """)
        
        proveedores_bd = [row['proveedor'] for row in cur.fetchall()]
        print(f"Se encontraron {len(proveedores_bd)} proveedores únicos en la base de datos")
        
        # 2. Crear mapeo de nombres (lowercase a nombre correcto)
        mapeo_proveedores = {}
        for prov_key in PROVEEDOR_CONFIG.keys():
            mapeo_proveedores[prov_key.lower()] = prov_key
        
        print(f"Mapeo de proveedores definido en PROVEEDOR_CONFIG: {len(mapeo_proveedores)} entradas")
        
        # 3. Identificar proveedores para normalizar
        normalizaciones = []
        for prov_bd in proveedores_bd:
            prov_lower = prov_bd.lower()
            if prov_lower in mapeo_proveedores and prov_bd != mapeo_proveedores[prov_lower]:
                normalizaciones.append({
                    'original': prov_bd,
                    'normalizado': mapeo_proveedores[prov_lower]
                })
        
        print(f"Se encontraron {len(normalizaciones)} proveedores para normalizar")
        
        # 4. Aplicar normalizaciones
        cambios_totales = 0
        for norm in normalizaciones:
            cur.execute("""
                UPDATE productos_manual 
                SET proveedor = %s 
                WHERE proveedor = %s
            """, (norm['normalizado'], norm['original']))
            
            filas_afectadas = cur.rowcount
            cambios_totales += filas_afectadas
            print(f"Normalización: '{norm['original']}' -> '{norm['normalizado']}' | {filas_afectadas} filas afectadas")
        
        print(f"Total de cambios realizados: {cambios_totales}")
        
        # 5. Verificar resultados
        cur.execute("""
            SELECT DISTINCT proveedor 
            FROM productos_manual 
            WHERE proveedor IS NOT NULL AND proveedor != ''
        """)
        
        proveedores_bd_despues = [row['proveedor'] for row in cur.fetchall()]
        print(f"Proveedores después de normalizar: {len(proveedores_bd_despues)}")
        
        # Cerrar conexión
        cur.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"[ERROR] Error al normalizar proveedores: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando normalización de proveedores en PostgreSQL...")
    resultado = normalizar_proveedores()
    print(f"Proceso finalizado con {'éxito' if resultado else 'errores'}")