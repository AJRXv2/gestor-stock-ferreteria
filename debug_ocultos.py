#!/usr/bin/env python3
import sys
from gestor import db_query

print('=== PROVEEDORES OCULTOS ===')
ocultos = db_query('SELECT * FROM proveedores_ocultos', fetch=True) or []
print(f'Total registros: {len(ocultos)}')
for row in ocultos:
    print(f'  - {row}')

print('\n=== PROVEEDORES OCULTOS PARA ferreteria_general ===')
ocultos_fg = db_query('SELECT LOWER(nombre) as nombre FROM proveedores_ocultos WHERE dueno=?', ('ferreteria_general',), fetch=True) or []
print(f'Total para ferreteria_general: {len(ocultos_fg)}')
ocultos_fg_set = {o['nombre'] for o in ocultos_fg}
print(f'Set de ocultos: {ocultos_fg_set}')

print(f'\nbermon está oculto: {"bermon" in ocultos_fg_set}')