#!/usr/bin/env python3
"""
Script de prueba para verificar que el dropdown muestra tanto proveedores Excel como Manual
"""

import sys
import os

# Agregar el directorio actual al path para importar gestor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestor import db_query, PROVEEDOR_CONFIG, DUENOS_CONFIG, get_excel_folder_for_dueno
    
    print("🔍 Verificando construcción del dropdown de proveedores...")
    
    # Simular la construcción de las listas como en agregar_producto
    proveedores_excel_ricky = []
    proveedores_excel_fg = []
    
    # 1) Excel por dueño
    for dueno in ['ricky', 'ferreteria_general']:
        if dueno in DUENOS_CONFIG:
            proveedores_dueno = DUENOS_CONFIG[dueno]['proveedores_excel']
            ocultos_excel = db_query("SELECT LOWER(nombre) as nombre FROM proveedores_ocultos WHERE dueno=?", (dueno,), fetch=True) or []
            ocultos_excel_set = {o['nombre'] for o in ocultos_excel}
            
            for key in proveedores_dueno:
                if key in PROVEEDOR_CONFIG and key.lower() not in ocultos_excel_set:
                    # Buscar archivos en la carpeta específica del dueño
                    carpeta_dueno = get_excel_folder_for_dueno(dueno)
                    if os.path.exists(carpeta_dueno):
                        archivos = [f for f in os.listdir(carpeta_dueno) if f.lower().startswith(key.lower()) and f.endswith('.xlsx') and f != 'productos_manual.xlsx']
                        if archivos:
                            dueno_display = 'Ricky' if dueno == 'ricky' else 'Ferretería General'
                            item = { 'key': key, 'nombre': key.title().replace('tools','Tools') + f' (Excel - {dueno_display})' }
                            if dueno == 'ricky':
                                proveedores_excel_ricky.append(item)
                            else:
                                proveedores_excel_fg.append(item)
    
    print(f"\n1. Proveedores Excel encontrados:")
    print(f"   Ricky: {len(proveedores_excel_ricky)}")
    for p in proveedores_excel_ricky:
        print(f"     - {p['nombre']} (key: {p['key']})")
    
    print(f"   Ferretería General: {len(proveedores_excel_fg)}")
    for p in proveedores_excel_fg:
        print(f"     - {p['nombre']} (key: {p['key']})")
    
    # 2) Manuales por dueño
    ocultos_rows = db_query("SELECT LOWER(nombre) as nombre, dueno FROM proveedores_ocultos", fetch=True) or []
    ocultos_pairs = {(o['nombre'], o['dueno']) for o in ocultos_rows}
    
    # Usar proveedores_duenos como fuente principal
    try:
        mappings = db_query("""
            SELECT pm.id, pm.nombre, pd.dueno 
            FROM proveedores_manual pm 
            JOIN proveedores_duenos pd ON pm.id = pd.proveedor_id 
            ORDER BY pm.nombre, pd.dueno
        """, fetch=True) or []
        print(f"\n2. Mappings de proveedores manuales encontrados: {len(mappings)}")
    except Exception as e:
        print(f"\n2. Error con proveedores_duenos: {e}")
        try:
            mappings = db_query("SELECT pm.id, pm.nombre, m.dueno FROM proveedores_manual pm JOIN proveedores_meta m ON LOWER(m.nombre)=LOWER(pm.nombre) ORDER BY pm.nombre, m.dueno", fetch=True) or []
            print(f"   Usando proveedores_meta fallback: {len(mappings)} mappings")
        except Exception as e2:
            print(f"   Ambas tablas fallan: {e2}")
            mappings = []
    
    # Agregar proveedores manuales a las listas
    for row in mappings:
        base = (row['nombre'] or '').strip()
        dueno_val = row['dueno']
        if (base.lower(), dueno_val) in ocultos_pairs:
            continue
        # Permitir tanto Excel como Manual para el mismo proveedor
        dueno_display = 'Ricky' if dueno_val == 'ricky' else 'Ferretería General'
        item = { 'key': f"manual_{row['id']}_{dueno_val}", 'nombre': f"{base} (Manual - {dueno_display})" }
        if dueno_val == 'ricky':
            proveedores_excel_ricky.append(item)
        else:
            proveedores_excel_fg.append(item)
    
    print(f"\n3. Lista final del dropdown:")
    print(f"   Ricky: {len(proveedores_excel_ricky)} proveedores")
    for p in proveedores_excel_ricky:
        print(f"     - {p['nombre']} (key: {p['key']})")
    
    print(f"   Ferretería General: {len(proveedores_excel_fg)} proveedores")
    for p in proveedores_excel_fg:
        print(f"     - {p['nombre']} (key: {p['key']})")
    
    # Verificar si Chiesa aparece en ambas versiones
    chiesa_excel = any('chiesa' in p['key'].lower() and 'excel' in p['nombre'].lower() for p in proveedores_excel_ricky)
    chiesa_manual = any('chiesa' in p['key'].lower() and 'manual' in p['nombre'].lower() for p in proveedores_excel_ricky)
    
    print(f"\n4. Verificación Chiesa:")
    print(f"   Chiesa (Excel): {'✅' if chiesa_excel else '❌'}")
    print(f"   Chiesa (Manual): {'✅' if chiesa_manual else '❌'}")
    
    if chiesa_excel and chiesa_manual:
        print(f"   ✅ ¡Perfecto! Chiesa aparece en ambas versiones")
    else:
        print(f"   ❌ Problema: Chiesa no aparece en ambas versiones")
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    print(traceback.format_exc())
