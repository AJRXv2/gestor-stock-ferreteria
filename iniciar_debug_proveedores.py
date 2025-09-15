"""
Script para iniciar la aplicación en modo debug y ejecutar pruebas.
"""
import os
import sys
import subprocess
import time
import webbrowser

def iniciar_app():
    """Inicia la aplicación Flask en modo debug."""
    print("\n=== INICIANDO APLICACIÓN EN MODO DEBUG ===\n")
    
    # Asegurarse de que estamos en el directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Establecer variables de entorno para Flask
    os.environ['FLASK_APP'] = 'gestor.py'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Comando para iniciar Flask
    cmd = ["python", "-m", "flask", "run"]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    print("\nPara detener la aplicación, presiona Ctrl+C en esta terminal.\n")
    
    # Abrir la página de diagnóstico de proveedores en el navegador
    url = "http://127.0.0.1:5000/debug_proveedores_ui"
    print(f"Abriendo en el navegador: {url}")
    
    # Dar tiempo para que el servidor Flask inicie
    time.sleep(1)
    webbrowser.open(url)
    
    # Iniciar el servidor Flask
    subprocess.run(cmd)

if __name__ == "__main__":
    iniciar_app()