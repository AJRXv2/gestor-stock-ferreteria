#!/usr/bin/env python3
import sys
import os
from gestor import DUENOS_CONFIG, PROVEEDOR_CONFIG, get_excel_folder_for_dueno

print('=== DEBUG COMPLETO DE PROVIDER LISTA ===')

# Simular el bucle exacto de la aplicación web
proveedores_excel_fg = []

# Para ferreteria_general específicamente
dueno = 'ferreteria_general'
print(f'\n🔄 Procesando dueño: {dueno}')

if dueno in DUENOS_CONFIG:
    proveedores_dueno = DUENOS_CONFIG[dueno]['proveedores_excel'] 
    print(f'  ✅ Proveedores configurados: {proveedores_dueno}')
    
    ocultos_excel = []  # Simulamos sin ocultos por ahora
    ocultos_excel_set = {o['nombre'] for o in ocultos_excel}
    print(f'  ⚠️ Proveedores ocultos: {ocultos_excel_set}')
    
    for key in proveedores_dueno:
        print(f'\n  🔍 Evaluando key: {key}')
        print(f'    - key in PROVEEDOR_CONFIG: {key in PROVEEDOR_CONFIG}')
        print(f'    - key.lower() not in ocultos_excel_set: {key.lower() not in ocultos_excel_set}')
        
        if key in PROVEEDOR_CONFIG and key.lower() not in ocultos_excel_set:
            carpeta_dueno = get_excel_folder_for_dueno(dueno)
            print(f'    - carpeta_dueno: {carpeta_dueno}')
            
            try:
                todos_archivos = os.listdir(carpeta_dueno)
                print(f'    - archivos en carpeta: {todos_archivos}')
                
                archivos = [f for f in todos_archivos if f.lower().startswith(key.lower()) and f.endswith('.xlsx') and f != 'productos_manual.xlsx']
                print(f'    - archivos filtrados para {key}: {archivos}')
                
                if archivos:
                    dueno_display = 'Ricky' if dueno == 'ricky' else 'Ferretería General'
                    item = { 'key': key, 'nombre': key.title().replace('tools','Tools') + f' ({dueno_display})' }
                    print(f'    - ✅ AGREGANDO ITEM: {item}')
                    proveedores_excel_fg.append(item)
                else:
                    print(f'    - ❌ NO se agregó {key}: no hay archivos')
            except Exception as e:
                print(f'    - ❌ ERROR al listar archivos: {e}')
        else:
            razones = []
            if key not in PROVEEDOR_CONFIG:
                razones.append('no está en PROVEEDOR_CONFIG')
            if key.lower() in ocultos_excel_set:
                razones.append('está en la lista de ocultos')
            print(f'    - ❌ NO se procesó {key}: {", ".join(razones)}')

print(f'\n📋 RESULTADO FINAL proveedores_excel_fg: {proveedores_excel_fg}')