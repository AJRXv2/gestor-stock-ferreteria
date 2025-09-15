#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico específico para problemas de búsqueda por proveedor
Este script crea un endpoint que simula la búsqueda con diferentes combinaciones
de parámetros para ayudar a identificar dónde está fallando la función.
"""

import os
import json
import sys
import time
import traceback
from flask import Blueprint, jsonify, request, current_app

# Blueprint para diagnóstico de búsqueda (para importar en gestor.py)
diagnostico_busqueda_bp = Blueprint('diagnostico_busqueda', __name__)

@diagnostico_busqueda_bp.route('/diagnostico_busqueda')
def diagnostico_busqueda_view():
    """Vista web para diagnóstico de problemas de búsqueda"""
    try:
        # Parámetros de la URL
        proveedor = request.args.get('proveedor', '')
        termino = request.args.get('termino', '')
        
        # Ejecutar diagnósticos
        resultados = ejecutar_diagnostico_busqueda(proveedor, termino)
        
        # Devolver resultados como JSON
        return jsonify(resultados)
    
    except Exception as e:
        traceback_info = traceback.format_exc()
        return jsonify({
            'error': True,
            'mensaje': f'Error durante el diagnóstico: {str(e)}',
            'traceback': traceback_info
        })

def ejecutar_diagnostico_busqueda(proveedor, termino):
    """Ejecutar diagnóstico de búsqueda con diferentes variaciones"""
    from gestor import (db_connect, db_query, execute_query, 
                       PROVEEDOR_CONFIG, buscar_en_excel, 
                       _is_postgres_configured)
    
    resultados = {
        'timestamp': time.time(),
        'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
        'ambiente': 'PostgreSQL' if _is_postgres_configured() else 'SQLite',
        'parametros': {
            'proveedor': proveedor,
            'termino': termino
        },
        'pruebas': {},
        'errores': []
    }
    
    try:
        # Información sobre PROVEEDOR_CONFIG
        resultados['proveedor_config'] = {
            'claves': list(PROVEEDOR_CONFIG.keys()),
            'claves_lower': [k.lower() for k in PROVEEDOR_CONFIG.keys()],
            'existe_proveedor': proveedor in PROVEEDOR_CONFIG,
            'existe_proveedor_case_insensitive': proveedor.lower() in [k.lower() for k in PROVEEDOR_CONFIG.keys()] if proveedor else False
        }
        
        # Si se proporcionó un proveedor, mostrar su configuración
        if proveedor:
            # Buscar proveedor de forma case-insensitive
            proveedor_key = None
            for k in PROVEEDOR_CONFIG.keys():
                if k.lower() == proveedor.lower():
                    proveedor_key = k
                    break
            
            if proveedor_key:
                # Encontrado - mostrar config
                config = PROVEEDOR_CONFIG[proveedor_key]
                resultados['proveedor_config']['encontrado'] = {
                    'clave_original': proveedor_key,
                    'nombre_mostrar': config.get('nombre_mostrar', ''),
                    'tiene_excel': config.get('tiene_excel', False),
                    'excel_sheet_name': config.get('excel_sheet_name', ''),
                    'columnas': list(config.get('columnas', {}).keys()) if isinstance(config.get('columnas'), dict) else [],
                    'columna_codigo': config.get('columna_codigo', ''),
                    'columna_descripcion': config.get('columna_descripcion', ''),
                    'columna_precio': config.get('columna_precio', ''),
                }
            else:
                # No encontrado
                resultados['proveedor_config']['encontrado'] = False
                resultados['errores'].append(f"Proveedor '{proveedor}' no encontrado en PROVEEDOR_CONFIG")
        
        # Pruebas de búsqueda en BD
        conn = db_connect()
        
        # 1. Búsqueda en la base de datos con nombre exacto del proveedor
        if proveedor:
            if _is_postgres_configured():
                # PostgreSQL usa parámetros %s
                query = "SELECT COUNT(*) as total FROM productos_manual WHERE proveedor = %s"
            else:
                # SQLite usa parámetros ?
                query = "SELECT COUNT(*) as total FROM productos_manual WHERE proveedor = ?"
                
            result = db_query(query, (proveedor,), conn=conn, fetch=True)
            resultados['pruebas']['bd_exacta'] = {
                'query': query,
                'parametros': [proveedor],
                'resultados': result[0]['total'] if result else 0
            }
            
            # 2. Búsqueda con LOWER (case insensitive)
            if _is_postgres_configured():
                query = "SELECT COUNT(*) as total FROM productos_manual WHERE LOWER(proveedor) = LOWER(%s)"
            else:
                query = "SELECT COUNT(*) as total FROM productos_manual WHERE LOWER(proveedor) = LOWER(?)"
                
            result = db_query(query, (proveedor,), conn=conn, fetch=True)
            resultados['pruebas']['bd_lower'] = {
                'query': query,
                'parametros': [proveedor],
                'resultados': result[0]['total'] if result else 0
            }
        
        # 3. Probar la función buscar_en_excel con diferentes variaciones
        if proveedor and termino:
            # Caso 1: Parámetros originales
            try:
                excel_results = buscar_en_excel(termino, provider_filtro=proveedor)
                resultados['pruebas']['excel_original'] = {
                    'parametros': {'termino': termino, 'proveedor': proveedor},
                    'resultados': len(excel_results),
                    'muestra': excel_results[:3] if excel_results else []
                }
            except Exception as e:
                resultados['errores'].append(f"Error en buscar_en_excel original: {str(e)}")
                resultados['pruebas']['excel_original'] = {'error': str(e)}
            
            # Caso 2: Convertir proveedor a minúsculas
            try:
                excel_results = buscar_en_excel(termino, provider_filtro=proveedor.lower())
                resultados['pruebas']['excel_lower'] = {
                    'parametros': {'termino': termino, 'proveedor': proveedor.lower()},
                    'resultados': len(excel_results),
                    'muestra': excel_results[:3] if excel_results else []
                }
            except Exception as e:
                resultados['errores'].append(f"Error en buscar_en_excel lower: {str(e)}")
                resultados['pruebas']['excel_lower'] = {'error': str(e)}
            
            # Caso 3: Usar mayúsculas
            try:
                excel_results = buscar_en_excel(termino, provider_filtro=proveedor.upper())
                resultados['pruebas']['excel_upper'] = {
                    'parametros': {'termino': termino, 'proveedor': proveedor.upper()},
                    'resultados': len(excel_results),
                    'muestra': excel_results[:3] if excel_results else []
                }
            except Exception as e:
                resultados['errores'].append(f"Error en buscar_en_excel upper: {str(e)}")
                resultados['pruebas']['excel_upper'] = {'error': str(e)}
                
        # 4. Buscar en todas las tablas para análisis completo
        if termino:
            try:
                from buscar_en_todas_tablas import buscar_en_todas_tablas
                
                # 4.1 Búsqueda sin filtro de proveedor
                resultados_todas = buscar_en_todas_tablas(termino, None)
                resultados['pruebas']['todas_tablas_sin_filtro'] = {
                    'parametros': {'termino': termino, 'proveedor': None},
                    'resultados': len(resultados_todas),
                    'muestra': resultados_todas[:3] if resultados_todas else []
                }
                
                # 4.2 Búsqueda con filtro de proveedor
                if proveedor:
                    resultados_todas = buscar_en_todas_tablas(termino, proveedor)
                    resultados['pruebas']['todas_tablas_con_filtro'] = {
                        'parametros': {'termino': termino, 'proveedor': proveedor},
                        'resultados': len(resultados_todas),
                        'muestra': resultados_todas[:3] if resultados_todas else []
                    }
            except Exception as e:
                resultados['errores'].append(f"Error en buscar_en_todas_tablas: {str(e)}")
        
        # 5. Verificar estructura y contenido de la tabla proveedores_manual
        try:
            if _is_postgres_configured():
                # PostgreSQL - obtener la estructura
                query_estructura = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'proveedores_manual'
                    ORDER BY ordinal_position
                """
                estructura = db_query(query_estructura, (), conn=conn, fetch=True)
                resultados['tablas'] = {
                    'proveedores_manual_estructura': [
                        {'columna': row['column_name'], 'tipo': row['data_type']}
                        for row in estructura
                    ]
                }
            else:
                # SQLite - obtener la estructura vía PRAGMA
                query_estructura = "PRAGMA table_info(proveedores_manual)"
                estructura = db_query(query_estructura, (), conn=conn, fetch=True)
                resultados['tablas'] = {
                    'proveedores_manual_estructura': [
                        {'columna': row['name'], 'tipo': row['type']} 
                        for row in estructura
                    ]
                }
                
            # Obtener datos de la tabla
            query_datos = "SELECT * FROM proveedores_manual LIMIT 10"
            datos = db_query(query_datos, (), conn=conn, fetch=True)
            
            resultados['tablas']['proveedores_manual_datos'] = [
                dict(row) for row in datos
            ]
                
        except Exception as e:
            resultados['errores'].append(f"Error al verificar estructura de tabla: {str(e)}")
    
    except Exception as e:
        resultados['errores'].append(f"Error general en diagnóstico: {str(e)}")
        resultados['traceback'] = traceback.format_exc()
    
    return resultados

# Para ejecución directa del script (fuera de Flask)
if __name__ == "__main__":
    print("Este script está diseñado para ser importado en gestor.py")
    print("Sin embargo, se puede ejecutar directamente para depuración")