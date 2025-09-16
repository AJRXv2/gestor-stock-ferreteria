#!/usr/bin/env python3
import requests
import sys

# Crear una sesión para manejar cookies
session = requests.Session()

print('=== VERIFICACIÓN DE TEMPLATE eliminar_manual.html ===')

# Hacer login
login_data = {
    'username': 'Pauluk',
    'password': 'Jap2005'
}

print('🔐 Haciendo login...')
login_response = session.post('http://localhost:5000/login', data=login_data)
print(f'Login status: {login_response.status_code}')

if login_response.status_code == 200:
    # Acceder a eliminar_manual
    print('📄 Accediendo a eliminar_manual...')
    response = session.get('http://localhost:5000/eliminar_manual')
    print(f'Eliminar manual status: {response.status_code}')
    
    if response.status_code == 200:
        html = response.text
        
        # Buscar la sección de backup
        print('\n🔍 Buscando sección de backup...')
        if 'Backup de Productos Manuales' in html:
            print('✅ Sección de backup encontrada en HTML')
        else:
            print('❌ Sección de backup NO encontrada en HTML')
        
        # Buscar botones específicos
        if 'Descargar Backup' in html:
            print('✅ Botón "Descargar Backup" encontrado')
        else:
            print('❌ Botón "Descargar Backup" NO encontrado')
        
        if 'Restaurar Backup' in html:
            print('✅ Botón "Restaurar Backup" encontrado')
        else:
            print('❌ Botón "Restaurar Backup" NO encontrado')
        
        # Buscar iconos Bootstrap
        if 'bi bi-download' in html:
            print('✅ Icono de descarga encontrado')
        else:
            print('❌ Icono de descarga NO encontrado')
        
        # Verificar estructura general
        backup_lines = []
        lines = html.split('\n')
        for i, line in enumerate(lines, 1):
            if 'backup' in line.lower() or 'Backup' in line:
                backup_lines.append((i, line.strip()))
        
        if backup_lines:
            print(f'\n📋 Líneas relacionadas con backup ({len(backup_lines)}):\n')
            for line_num, line_content in backup_lines[:10]:  # Primeras 10
                content = line_content[:100] + '...' if len(line_content) > 100 else line_content
                print(f'  {line_num}: {content}')
        else:
            print('\n❌ No se encontraron líneas relacionadas con backup')
    
    else:
        print(f'❌ Error: Status code {response.status_code}')
        print(response.text[:500])
else:
    print(f'❌ Error en login: {login_response.status_code}')