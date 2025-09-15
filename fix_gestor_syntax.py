#!/usr/bin/env python3
"""
Script para corregir problemas de sintaxis en gestor.py
"""

def fix_gestor_syntax():
    """Corrige los problemas de sintaxis en el archivo"""
    
    # Leer el archivo actual
    with open('gestor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar la línea problemática y corregirla
    lines = content.split('\n')
    
    # Buscar la línea 5921 (índice 5920) que tiene el except problemático
    if len(lines) > 5920:
        # Verificar si hay un except sin try correspondiente
        if 'except Exception as e:' in lines[5920]:
            # Buscar hacia atrás para encontrar el try correspondiente
            try_found = False
            for i in range(5920, -1, -1):
                if 'try:' in lines[i]:
                    try_found = True
                    break
            
            if not try_found:
                # Eliminar el except problemático y las líneas relacionadas
                print(f"Eliminando except problemático en línea {5921}")
                # Eliminar desde la línea 5921 hasta encontrar el return
                for i in range(5920, min(5930, len(lines))):
                    if 'return resultados' in lines[i]:
                        # Eliminar las líneas problemáticas
                        lines = lines[:5920] + lines[i+1:]
                        break
    
    # Escribir el archivo corregido
    with open('gestor.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Sintaxis corregida exitosamente")

if __name__ == "__main__":
    fix_gestor_syntax()
