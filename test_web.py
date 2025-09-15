#!/usr/bin/env python3
import requests
import sys

# Crear una sesión para manejar cookies
session = requests.Session()

print('=== TESTEO DIRECTO DE PÁGINA ===')

# Primero hacer login
login_data = {
    'username': 'Pauluk',
    'password': 'Jap2005'
}

print('🔐 Haciendo login...')
login_response = session.post('http://localhost:5000/login', data=login_data)
print(f'Login status: {login_response.status_code}')

# Ahora acceder a agregar_producto
print('📄 Accediendo a agregar_producto...')
response = session.get('http://localhost:5000/agregar_producto')
print(f'Agregar producto status: {response.status_code}')

if response.status_code == 200:
    html = response.text
    
    # Buscar menciones de bermon
    bermon_mentions = []
    lines = html.split('\n')
    for i, line in enumerate(lines, 1):
        if 'bermon' in line.lower():
            bermon_mentions.append((i, line.strip()))

    print(f'\n🔍 Menciones de "bermon": {len(bermon_mentions)}')
    for line_num, line_content in bermon_mentions:
        content = line_content[:150] + '...' if len(line_content) > 150 else line_content
        print(f'  Línea {line_num}: {content}')

    # Buscar todas las opciones de select de ferretería general
    fg_options = []
    for i, line in enumerate(lines, 1):
        if '<option' in line.lower() and 'ferretería general' in line.lower():
            fg_options.append((i, line.strip()))

    print(f'\n📋 Opciones de Ferretería General: {len(fg_options)}')
    for line_num, line_content in fg_options:
        content = line_content[:150] + '...' if len(line_content) > 150 else line_content
        print(f'  Línea {line_num}: {content}')

else:
    print(f'❌ Error: Status code {response.status_code}')
    print(response.text[:500])