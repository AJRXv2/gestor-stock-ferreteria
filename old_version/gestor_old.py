import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import glob

# --- Configuración de la Aplicación ---
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Clave para mensajes flash

# --- Rutas de Archivos y Carpetas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'stock.db')
EXCEL_FOLDER = os.path.join(BASE_DIR, 'listas_excel')

# --- Funciones de Base de Datos ---
def init_db():
    """Inicializa la base de datos y crea la tabla si no existe."""
    if not os.path.exists(EXCEL_FOLDER):
        os.makedirs(EXCEL_FOLDER)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha_compra TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def db_query(query, params=()):
    """Ejecuta una consulta en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    if query.strip().upper().startswith('SELECT'):
        result = [dict(row) for row in cursor.fetchall()]
    else:
        conn.commit()
        result = None
    conn.close()
    return result

# --- Funciones de Lógica de Negocio ---
def buscar_en_excel(termino_busqueda):
    """Busca un producto en todos los archivos Excel de la carpeta 'listas_excel'."""
    resultados = []
    archivos_excel = glob.glob(os.path.join(EXCEL_FOLDER, '*.xlsx'))
    
    if not archivos_excel:
        return resultados

    for archivo in archivos_excel:
        try:
            df = pd.read_excel(archivo)
            # Asumimos que las columnas relevantes se llaman 'codigo' y 'nombre'
            # El usuario deberá ajustar estos nombres si son diferentes en sus archivos
            df.columns = [col.strip().lower() for col in df.columns]
            
            # Buscar por nombre o código (ajustar nombres de columna si es necesario)
            filtro = df[
                df['nombre'].str.contains(termino_busqueda, case=False, na=False) |
                (df['codigo'].astype(str).str.contains(termino_busqueda, case=False, na=False) if 'codigo' in df.columns else pd.Series([False]*len(df)))
            ]
            
            for _, row in filtro.iterrows():
                resultados.append(row.to_dict())
        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")
            
    return resultados

# --- Rutas de la Aplicación Web (Flask) ---
@app.route('/')
def index():
    """Página principal que muestra el historial de stock."""
    termino = request.args.get('q', '')
    if termino:
        productos = db_query(
            "SELECT * FROM stock WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY fecha_compra DESC",
            (f'%{termino}%', f'%{termino}%')
        )
    else:
        productos = db_query("SELECT * FROM stock ORDER BY fecha_compra DESC")
        
    return render_template('index.html', productos=productos, termino_busqueda=termino)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    """Página para buscar en Excel o agregar manualmente un producto."""
    if request.method == 'POST':
        # Lógica para agregar una compra a la base de datos
        try:
            db_query(
                "INSERT INTO stock (codigo, nombre, precio, cantidad, fecha_compra) VALUES (?, ?, ?, ?, ?)",
                (
                    request.form.get('codigo'),
                    request.form['nombre'],
                    float(request.form['precio']),
                    int(request.form['cantidad']),
                    request.form['fecha_compra']
                )
            )
            flash('Producto agregado al stock con éxito.', 'success')
        except (ValueError, KeyError) as e:
            flash(f'Error en los datos del formulario: {e}', 'danger')
        return redirect(url_for('index'))

    # Lógica para buscar en Excel
    termino_excel = request.args.get('busqueda_excel', '')
    resultados_excel = []
    if termino_excel:
        resultados_excel = buscar_en_excel(termino_excel)

    return render_template('agregar.html', resultados_excel=resultados_excel, termino_excel=termino_excel, fecha_actual=datetime.now().strftime('%Y-%m-%d'))

@app.route('/actualizar_stock/<int:id>', methods=['POST'])
def actualizar_stock(id):
    """Actualiza la cantidad de un producto en el stock (resta)."""
    try:
        cantidad_vendida = int(request.form['cantidad_vendida'])
        producto_actual = db_query("SELECT cantidad FROM stock WHERE id = ?", (id,))[0]
        
        if cantidad_vendida <= 0:
            flash('La cantidad vendida debe ser mayor que cero.', 'warning')
        elif cantidad_vendida > producto_actual['cantidad']:
            flash('No se puede vender más de la cantidad disponible en stock.', 'danger')
        else:
            nueva_cantidad = producto_actual['cantidad'] - cantidad_vendida
            db_query("UPDATE stock SET cantidad = ? WHERE id = ?", (nueva_cantidad, id))
            flash('Stock actualizado correctamente.', 'success')
            
    except (ValueError, IndexError):
        flash('Error al actualizar el stock. Verifique los datos.', 'danger')
        
    return redirect(url_for('index'))

# --- Plantillas HTML (deben ir en una carpeta 'templates') ---
# Crear un archivo 'templates/base.html'
"""
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gestor de Stock</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 1200px; }
        .card { margin-bottom: 1.5rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">Gestor de Stock</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Inicio / Historial</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('agregar_producto') }}">Agregar Producto</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Crear un archivo 'templates/index.html'
"""
{% extends 'base.html' %}

{% block content %}
<div class="card">
    <div class="card-header">
        <h3>Historial y Gestión de Stock</h3>
    </div>
    <div class="card-body">
        <form method="get" action="{{ url_for('index') }}" class="mb-4">
            <div class="input-group">
                <input type="text" name="q" class="form-control" placeholder="Buscar por nombre o código..." value="{{ termino_busqueda }}">
                <button class="btn btn-primary" type="submit">Buscar</button>
                <a href="{{ url_for('index') }}" class="btn btn-secondary">Limpiar</a>
            </div>
        </form>

        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Fecha Compra</th>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Precio Unit.</th>
                        <th>Cantidad Actual</th>
                        <th>Acción (Venta)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in productos %}
                    <tr>
                        <td>{{ p.fecha_compra }}</td>
                        <td>{{ p.codigo or 'N/A' }}</td>
                        <td>{{ p.nombre }}</td>
                        <td>${{ "%.2f"|format(p.precio) }}</td>
                        <td><strong>{{ p.cantidad }}</strong></td>
                        <td>
                            {% if p.cantidad > 0 %}
                            <form method="post" action="{{ url_for('actualizar_stock', id=p.id) }}" class="d-flex">
                                <input type="number" name="cantidad_vendida" class="form-control form-control-sm me-2" placeholder="Cant." min="1" max="{{ p.cantidad }}" required style="width: 80px;">
                                <button type="submit" class="btn btn-success btn-sm">Vender</button>
                            </form>
                            {% else %}
                            <span class="badge bg-danger">Sin Stock</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="text-center">No hay productos en el stock. Comience agregando uno.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""

# Crear un archivo 'templates/agregar.html'
"""
{% extends 'base.html' %}

{% block content %}
<div class="row">
    <!-- Columna para buscar en Excel -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h4>1. Buscar Producto en Listas de Precios (Excel)</h4></div>
            <div class="card-body">
                <form method="get" action="{{ url_for('agregar_producto') }}">
                    <div class="input-group mb-3">
                        <input type="text" name="busqueda_excel" class="form-control" placeholder="Nombre o código del producto" value="{{ termino_excel }}">
                        <button class="btn btn-info" type="submit">Buscar en Excel</button>
                    </div>
                </form>
                {% if termino_excel %}
                    <h5>Resultados para "{{ termino_excel }}"</h5>
                    {% if resultados_excel %}
                    <ul class="list-group">
                        {% for r in resultados_excel %}
                        <li class="list-group-item">
                            {{ r.nombre }} ({{ r.codigo or 'S/C' }}) - ${{ r.precio or 'S/P' }}
                            <button class="btn btn-sm btn-primary float-end" onclick="cargarFormulario('{{ r.codigo or '' }}', '{{ r.nombre }}', '{{ r.precio or 0 }}')">Seleccionar</button>
                        </li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <p class="text-muted">No se encontraron resultados en los archivos de Excel.</p>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Columna para agregar al stock -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h4>2. Agregar Compra al Stock</h4></div>
            <div class="card-body">
                <p class="text-muted">Seleccione un producto de la izquierda o complete los campos manualmente.</p>
                <form id="form-agregar" method="post" action="{{ url_for('agregar_producto') }}">
                    <div class="mb-3">
                        <label for="fecha_compra" class="form-label">Fecha de Compra</label>
                        <input type="date" id="fecha_compra" name="fecha_compra" class="form-control" value="{{ fecha_actual }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="codigo" class="form-label">Código (Opcional)</label>
                        <input type="text" id="codigo" name="codigo" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="nombre" class="form-label">Nombre del Producto</label>
                        <input type="text" id="nombre" name="nombre" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="precio" class="form-label">Precio de Compra</label>
                        <input type="number" id="precio" name="precio" class="form-control" step="0.01" min="0" required>
                    </div>
                    <div class="mb-3">
                        <label for="cantidad" class="form-label">Cantidad Comprada</label>
                        <input type="number" id="cantidad" name="cantidad" class="form-control" min="1" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">Añadir al Stock</button>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
function cargarFormulario(codigo, nombre, precio) {
    document.getElementById('codigo').value = codigo;
    document.getElementById('nombre').value = nombre;
    document.getElementById('precio').value = parseFloat(precio) || 0;
    document.getElementById('cantidad').focus();
}
</script>
{% endblock %}
"""

# --- Ejecución de la Aplicación ---
if __name__ == '__main__':
    init_db()  # Asegura que la DB y carpetas existan al iniciar
    # Para desarrollo:
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    # Para producción con Waitress (ejecutar este bloque en un script separado o condicionalmente):
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8080)
