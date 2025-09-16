#!/usr/bin/env python3
import requests
import os

# Crear una sesión para manejar cookies
session = requests.Session()

print('=== TESTEO DE BACKUP EXCEL MANUAL ===')

# Hacer login
login_data = {
    'username': 'Pauluk',
    'password': 'Jap2005'
}

print('🔐 Haciendo login...')
login_response = session.post('http://localhost:5000/login', data=login_data)
print(f'Login status: {login_response.status_code}')

if login_response.status_code == 200:
    # Probar descarga de backup
    print('\n📥 Probando descarga de backup...')
    backup_response = session.get('http://localhost:5000/descargar_backup_manual')
    print(f'Descarga status: {backup_response.status_code}')
    
    if backup_response.status_code == 200:
        # Verificar headers del archivo
        content_disposition = backup_response.headers.get('Content-Disposition', '')
        content_type = backup_response.headers.get('Content-Type', '')
        
        print(f'Content-Type: {content_type}')
        print(f'Content-Disposition: {content_disposition}')
        print(f'Tamaño del archivo: {len(backup_response.content)} bytes')
        
        # Guardar archivo para verificar
        if content_disposition and 'productos_manual_backup_' in content_disposition:
            print('✅ El archivo de backup se generó correctamente')
        else:
            print('❌ Error en el formato del archivo de backup')
    else:
        print(f'❌ Error en descarga: {backup_response.status_code}')
        print(backup_response.text[:500])
else:
    print(f'❌ Error en login: {login_response.status_code}')

print('\n🔍 Verificando archivos productos_manual.xlsx existentes...')
# Verificar si existen archivos productos_manual.xlsx
listas_excel = 'C:/Users/alexp/Documents/gestor_stock/listas_excel'
for carpeta in ['ricky', 'ferreteria_general']:
    archivo_path = os.path.join(listas_excel, carpeta, 'productos_manual.xlsx')
    if os.path.exists(archivo_path):
        size = os.path.getsize(archivo_path)
        print(f'✅ Encontrado: {archivo_path} ({size} bytes)')
    else:
        print(f'❌ No encontrado: {archivo_path}')