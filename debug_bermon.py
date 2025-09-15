#!/usr/bin/env python3
import sys
import os
from gestor import DUENOS_CONFIG, PROVEEDOR_CONFIG, get_excel_folder_for_dueno

print('=== DEBUG BERMON ===')
dueno = 'ferreteria_general'
print(f'Proveedores de {dueno}: {DUENOS_CONFIG[dueno]["proveedores_excel"]}')

carpeta_dueno = get_excel_folder_for_dueno(dueno)
print(f'Carpeta: {carpeta_dueno}')

key = 'bermon'
print(f'\nBuscando archivos para: {key}')
print(f'key in PROVEEDOR_CONFIG: {key in PROVEEDOR_CONFIG}')

try:
    archivos = [f for f in os.listdir(carpeta_dueno) if f.lower().startswith(key.lower()) and f.endswith('.xlsx') and f != 'productos_manual.xlsx']
    print(f'Archivos encontrados: {archivos}')
except FileNotFoundError:
    print(f'Error: No se encontró la carpeta {carpeta_dueno}')
    archivos = []

# Simular el proceso completo
if key in PROVEEDOR_CONFIG and archivos:
    dueno_display = 'Ferretería General'
    item = { 'key': key, 'nombre': key.title().replace('tools','Tools') + f' ({dueno_display})' }
    print(f'\nItem generado: {item}')
else:
    print('\nNo se cumplieron las condiciones para agregar el item')
    print(f'  - key in PROVEEDOR_CONFIG: {key in PROVEEDOR_CONFIG}')
    print(f'  - archivos: {archivos}')