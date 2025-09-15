#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para problemas de filtrado por proveedor en Railway
Este script es accesible vía web y muestra información detallada sobre las tablas,
estructuras y datos relacionados con proveedores en la base de datos PostgreSQL.
"""

import os
import json
import sys
import time
import traceback
from flask import Blueprint, jsonify, request, current_app

# Blueprint para los diagnósticos (para importar en gestor.py)
diagnostico_railway_bp = Blueprint('diagnostico_railway', __name__)

@diagnostico_railway_bp.route('/diagnostico_railway')
def diagnostico_railway_view():
    """Vista web para diagnóstico de Railway"""
    try:
        # Verificar si estamos en PostgreSQL
        if not _is_postgres_configured():
            return jsonify({
                'error': True,
                'mensaje': 'Este diagnóstico solo funciona en entorno PostgreSQL (Railway)',
                'ambiente': 'SQLite (local)'
            })
        
        # Recopilar información de diagnóstico
        resultados = ejecutar_diagnostico_railway()
        
        # Devolver resultados como JSON
        return jsonify(resultados)
    
    except Exception as e:
        traceback_info = traceback.format_exc()
        return jsonify({
            'error': True,
            'mensaje': f'Error durante el diagnóstico: {str(e)}',
            'traceback': traceback_info
        })

def _is_postgres_configured():
    """Verificar si el entorno tiene PostgreSQL configurado"""
    # Esta función debe coincidir con la de gestor.py
    try:
        HAS_POSTGRES = False
        try:
            import psycopg2
            HAS_POSTGRES = True
        except ImportError:
            HAS_POSTGRES = False
            
        return all(os.environ.get(k) for k in ['DATABASE_URL']) and HAS_POSTGRES
    except:
        return False

def ejecutar_diagnostico_railway():
    """Ejecutar diagnóstico completo de Railway"""
    import psycopg2
    import psycopg2.extras
    
    resultados = {
        'timestamp': time.time(),
        'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
        'ambiente': 'PostgreSQL (Railway)',
        'errores': [],
        'tablas': {},
        'consultas': {},
        'proveedor_config': {}
    }
    
    # Conectar a la base de datos
    try:
        dsn = os.environ.get('DATABASE_URL', '')
        if dsn.startswith('postgres://'):
            dsn = dsn.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(dsn)
        conn.set_session(autocommit=True)
        
        # Usar cursor de diccionario para obtener resultados con nombres de columnas
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 1. Verificar tablas existentes
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        resultados['tablas']['lista'] = [row['table_name'] for row in cur.fetchall()]
        
        # 2. Verificar estructura de tablas críticas
        tablas_criticas = ['proveedores_manual', 'proveedores_duenos', 'productos_manual']
        for tabla in tablas_criticas:
            if tabla in resultados['tablas']['lista']:
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{tabla}'
                    ORDER BY ordinal_position
                """)
                resultados['tablas'][tabla] = [
                    {'columna': row['column_name'], 'tipo': row['data_type']}
                    for row in cur.fetchall()
                ]
            else:
                resultados['errores'].append(f"Tabla crítica '{tabla}' no existe")
        
        # 3. Contar registros en tablas principales
        for tabla in tablas_criticas + ['proveedores_meta', 'users']:
            if tabla in resultados['tablas']['lista']:
                cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                row = cur.fetchone()
                resultados['tablas'][f'{tabla}_count'] = row['total'] if row else 0
        
        # 4. Muestreo de datos de proveedores
        if 'proveedores_manual' in resultados['tablas']['lista']:
            cur.execute("""
                SELECT id, nombre, dueno
                FROM proveedores_manual
                ORDER BY id
                LIMIT 20
            """)
            resultados['consultas']['proveedores_muestra'] = [
                dict(row) for row in cur.fetchall()
            ]
        
        # 5. Muestreo de relación proveedores-dueños
        if 'proveedores_duenos' in resultados['tablas']['lista']:
            cur.execute("""
                SELECT pd.id, pd.proveedor_id, pd.dueno, pm.nombre as proveedor_nombre
                FROM proveedores_duenos pd
                LEFT JOIN proveedores_manual pm ON pd.proveedor_id = pm.id
                ORDER BY pd.id
                LIMIT 20
            """)
            resultados['consultas']['proveedores_duenos_muestra'] = [
                dict(row) for row in cur.fetchall()
            ]
        
        # 6. Verificar índices
        cur.execute("""
            SELECT
                t.relname as table_name,
                i.relname as index_name,
                a.attname as column_name
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND t.relname in ('proveedores_manual', 'proveedores_duenos', 'productos_manual')
            ORDER BY
                t.relname,
                i.relname
        """)
        resultados['tablas']['indices'] = [
            {
                'tabla': row['table_name'], 
                'indice': row['index_name'], 
                'columna': row['column_name']
            }
            for row in cur.fetchall()
        ]
        
        # 7. Probar consultas de búsqueda
        # Ejemplo simple buscando productos de un proveedor específico
        if 'productos_manual' in resultados['tablas']['lista']:
            # Buscar un proveedor existente para la prueba
            cur.execute("SELECT nombre FROM proveedores_manual LIMIT 1")
            proveedor_prueba = cur.fetchone()
            
            if proveedor_prueba:
                nombre_proveedor = proveedor_prueba['nombre']
                
                # Consulta normal (sin aplicar fix)
                cur.execute(f"""
                    SELECT COUNT(*) as total
                    FROM productos_manual 
                    WHERE proveedor = '{nombre_proveedor}'
                """)
                resultados['consultas']['busqueda_exacta'] = {
                    'proveedor': nombre_proveedor,
                    'resultados': cur.fetchone()['total']
                }
                
                # Consulta con lowercase (aplicando fix)
                cur.execute(f"""
                    SELECT COUNT(*) as total
                    FROM productos_manual 
                    WHERE LOWER(proveedor) = LOWER('{nombre_proveedor}')
                """)
                resultados['consultas']['busqueda_lowercase'] = {
                    'proveedor': nombre_proveedor,
                    'resultados': cur.fetchone()['total']
                }
            
            # 8. Obtener valores PROVEEDOR_CONFIG
            try:
                # Recrear la lógica del PROVEEDOR_CONFIG de gestor.py
                from gestor import PROVEEDOR_CONFIG
                # Convertir a diccionario serializable
                resultados['proveedor_config'] = {
                    k: {
                        'nombre_mostrar': v.get('nombre_mostrar', ''),
                        'tiene_excel': v.get('tiene_excel', False),
                        'excel_sheet_name': v.get('excel_sheet_name', ''),
                        'columnas': v.get('columnas', {}),
                        'columna_codigo': v.get('columna_codigo', ''),
                        'columna_descripcion': v.get('columna_descripcion', ''),
                        'columna_precio': v.get('columna_precio', ''),
                        'sin_stock': v.get('sin_stock', [])
                    }
                    for k, v in PROVEEDOR_CONFIG.items()
                }
            except Exception as e:
                resultados['errores'].append(f"Error al obtener PROVEEDOR_CONFIG: {e}")
                
        # 9. Verificar consistencia de datos
        # Buscar proveedores que existan en productos pero no en la tabla de proveedores
        cur.execute("""
            SELECT DISTINCT proveedor 
            FROM productos_manual 
            WHERE proveedor IS NOT NULL 
            AND proveedor != ''
        """)
        proveedores_en_productos = [row['proveedor'].lower() for row in cur.fetchall()]
        
        cur.execute("SELECT LOWER(nombre) as nombre_lower FROM proveedores_manual")
        proveedores_registrados = [row['nombre_lower'] for row in cur.fetchall()]
        
        proveedores_faltantes = [p for p in proveedores_en_productos if p not in proveedores_registrados]
        resultados['consultas']['proveedores_inconsistentes'] = proveedores_faltantes
        
        # Cerrar conexión
        cur.close()
        conn.close()
    
    except Exception as e:
        resultados['errores'].append(f"Error en diagnóstico: {str(e)}")
        resultados['traceback'] = traceback.format_exc()
    
    return resultados

# Para ejecución directa del script (fuera de Flask)
if __name__ == "__main__":
    print("Este script está diseñado para ser importado en gestor.py")
    print("Sin embargo, se puede ejecutar directamente para depuración")
    
    try:
        if _is_postgres_configured():
            resultados = ejecutar_diagnostico_railway()
            print(json.dumps(resultados, indent=2, ensure_ascii=False))
        else:
            print("Este script solo funciona en entorno PostgreSQL (Railway)")
            print("DATABASE_URL no está configurado o psycopg2 no está instalado")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()