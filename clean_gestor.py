#!/usr/bin/env python3
"""
Script para limpiar el archivo gestor.py eliminando código residual
"""

def clean_gestor_file():
    """Limpia el archivo gestor.py eliminando código residual"""
    
    # Leer el archivo actual
    with open('gestor.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar las líneas problemáticas y eliminarlas
    cleaned_lines = []
    skip_until_function = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si encontramos código residual mal indentado, lo saltamos
        if line_num == 5758 and 'if termino_busqueda.lower() in codigo:' in line:
            print(f"Saltando línea {line_num}: {line.strip()}")
            skip_until_function = True
            continue
            
        # Si estamos saltando líneas, continuar hasta encontrar una función
        if skip_until_function:
            if line.strip().startswith('def ') and '(' in line:
                skip_until_function = False
                cleaned_lines.append(line)
            else:
                print(f"Saltando línea {line_num}: {line.strip()}")
                continue
        
        # Si encontramos otras líneas problemáticas, saltarlas
        if (line_num >= 5758 and line_num <= 6000 and 
            ('[EXCEL DEBUG]' in line or 
             'df = pd.read_excel' in line or
             'df.rename(columns' in line or
             'if df.empty:' in line or
             'print(f"[EXCEL ERROR]' in line or
             'return resultados' in line and not line.strip().startswith('return'))):
            print(f"Saltando línea {line_num}: {line.strip()}")
            continue
            
        cleaned_lines.append(line)
    
    # Escribir el archivo limpio
    with open('gestor.py', 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print("✅ Archivo limpiado exitosamente")

if __name__ == "__main__":
    clean_gestor_file()
