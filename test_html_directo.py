#!/usr/bin/env python3
import requests
import re

# Crear una sesión para manejar cookies
session = requests.Session()

print('=== TEST DIRECTO DE HTML RENDERIZADO ===')

# Hacer login
login_data = {
    'username': 'Pauluk',
    'password': 'Jap2005'
}

print('🔐 Haciendo login...')
login_response = session.post('http://localhost:5000/login', data=login_data)

if login_response.status_code == 200:
    print('📄 Obteniendo HTML de eliminar_manual...')
    response = session.get('http://localhost:5000/eliminar_manual')
    
    if response.status_code == 200:
        html = response.text
        
        # Buscar la sección específica de backup
        print('\n🔍 Buscando sección de backup...')
        
        # Extraer la sección de backup
        backup_start = html.find('Backup')
        if backup_start != -1:
            backup_section = html[backup_start-100:backup_start+800]  # Contexto amplio
            print('📋 SECCIÓN BACKUP ENCONTRADA:')
            print('=' * 60)
            print(backup_section)
            print('=' * 60)
        else:
            print('❌ No se encontró sección de backup')
        
        # Buscar específicamente por dueno_destino
        if 'dueno_destino' in html:
            print('\n🚨 ENCONTRADO dueno_destino en HTML!')
            # Encontrar todas las ocurrencias
            lines = html.split('\n')
            for i, line in enumerate(lines, 1):
                if 'dueno_destino' in line:
                    print(f'  Línea {i}: {line.strip()}')
        else:
            print('\n✅ NO se encontró dueno_destino en HTML')
        
        # Buscar por "Destino:"
        if 'Destino:' in html:
            print('\n🚨 ENCONTRADO "Destino:" en HTML!')
            lines = html.split('\n')
            for i, line in enumerate(lines, 1):
                if 'Destino:' in line:
                    print(f'  Línea {i}: {line.strip()}')
        else:
            print('\n✅ NO se encontró "Destino:" en HTML')
            
        # Buscar el comentario que agregamos
        if 'ARCHIVO COMPARTIDO SIN DESTINO' in html:
            print('\n✅ Comentario de actualización encontrado - template está actualizado')
        else:
            print('\n❌ Comentario de actualización NO encontrado - template puede no estar actualizado')
            
    else:
        print(f'❌ Error al obtener página: {response.status_code}')
else:
    print(f'❌ Error en login: {login_response.status_code}')