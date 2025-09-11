# gestor.py (completo, corregido)
import os
import mysql.connector
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import glob
import re
try:
    from flask_wtf import CSRFProtect
    from flask_wtf.csrf import generate_csrf
    _HAS_FLASK_WTF = True
except Exception:
    # Flask-WTF not available, provide a minimal fallback
    CSRFProtect = None
    _HAS_FLASK_WTF = False
    def generate_csrf():
        # lazy import to avoid top-level secret import when not needed
        import secrets
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_urlsafe(16)
        return session['_csrf_token']
from decimal import Decimal, InvalidOperation
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

# --- Configuración de la Aplicación ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
app.permanent_session_lifetime = timedelta(hours=3)

if _HAS_FLASK_WTF:
    # Use Flask-WTF CSRFProtect when available
    csrf = CSRFProtect(app)
    # Expose generate_csrf to templates as csrf_token()
    app.jinja_env.globals['csrf_token'] = generate_csrf
else:
    # Fallback: expose our simple generate_csrf and validate on POST
    app.jinja_env.globals['csrf_token'] = generate_csrf

    @app.before_request
    def csrf_protect_fallback():
        if request.method == 'POST':
            token = session.get('_csrf_token')
            if not token:
                import secrets
                session['_csrf_token'] = secrets.token_urlsafe(16)
                token = session['_csrf_token']

            form_token = request.form.get('csrf_token')
            header_token = request.headers.get('X-CSRFToken') or request.headers.get('X-CSRF-Token')
            json_token = None
            if request.is_json:
                try:
                    data = request.get_json(silent=True) or {}
                    json_token = data.get('csrf_token')
                except Exception:
                    json_token = None

            if form_token == token or header_token == token or json_token == token:
                return

            if request.is_json:
                return jsonify({'success': False, 'error': 'CSRF token inválido o ausente.'}), 400
            flash('CSRF token inválido o ausente.', 'danger')
            if 'user_id' in session:
                return redirect(url_for('index'))
            return redirect(url_for('login'))

# --- Rutas de Archivos y Carpetas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FOLDER = os.path.join(BASE_DIR, 'listas_excel')
MANUAL_PRODUCTS_FILE = os.path.join(EXCEL_FOLDER, 'productos_manual.xlsx')

# --- Funciones de Utilidad ---
def parse_price(price_str):
    """
    Interpreta precios con distintos formatos:
    - 200.000 -> 200000
    - 200,50  -> 200.50
    - 200.000,75 -> 200000.75
    - 200,000.75 -> 200000.75 (formato inglés)
    Devuelve (float, texto_error)
    """
    if price_str is None:
        return 0.0, ''
    if not isinstance(price_str, str) or not price_str.strip():
        return 0.0, ''

    cleaned_str = price_str.replace('$', '').replace(' ', '').strip()

    # Caso: contiene tanto punto como coma
    if '.' in cleaned_str and ',' in cleaned_str:
        # Si la coma está después del último punto asumimos formato español: 200.000,75
        if cleaned_str.rfind(',') > cleaned_str.rfind('.'):
            cleaned_str = cleaned_str.replace('.', '').replace(',', '.')
        else:
            # Caso inglés: 200,000.75
            cleaned_str = cleaned_str.replace(',', '')
    elif ',' in cleaned_str:
        # Solo coma: decimal
        cleaned_str = cleaned_str.replace(',', '.')
    else:
        # Solo puntos: probablemente separadores de miles
        # Si hay más de un punto o el segmento después del punto tiene 3 dígitos, quitar puntos
        if cleaned_str.count('.') > 1 or (cleaned_str.count('.') == 1 and len(cleaned_str.split('.')[1]) == 3):
            cleaned_str = cleaned_str.replace('.', '')

    try:
        return float(cleaned_str), ''
    except (ValueError, TypeError):
        return 0.0, price_str

# --- Funciones de Base de Datos ---
def get_db_connection():
    # Try to read DB credentials from environment first
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')

    # If any credential is missing, attempt to load them from PythonAnywhere WSGI files
    # (some PythonAnywhere setups place os.environ[...] assignments in the wsgi file)
    if not db_host or not db_name or not db_user or not db_pass:
        try:
            _loaded = False
            # Look for common wsgi file patterns on PythonAnywhere
            for candidate in glob.glob('/var/www/*_wsgi.py'):
                try:
                    with open(candidate, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    # Regex to capture os.environ['VAR'] = 'value' or "value"
                    for var in ('DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASS', 'SECRET_KEY'):
                        m = re.search(r"os\.environ\[['\"]%s['\"]\]\s*=\s*['\"]([^'\"]+)['\"]" % var, content)
                        if m:
                            # don't overwrite an existing env var that is set
                            if os.getenv(var) is None:
                                os.environ[var] = m.group(1)
                                _loaded = True
                except Exception:
                    continue
            # Also try the more generic /var/www/*.py files if none found
            if not _loaded:
                for candidate in glob.glob('/var/www/*.py'):
                    try:
                        with open(candidate, 'r', encoding='utf-8') as fh:
                            content = fh.read()
                        for var in ('DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASS', 'SECRET_KEY'):
                            m = re.search(r"os\.environ\[['\"]%s['\"]\]\s*=\s*['\"]([^'\"]+)['\"]" % var, content)
                            if m:
                                if os.getenv(var) is None:
                                    os.environ[var] = m.group(1)
                                    _loaded = True
                    except Exception:
                        continue
        except Exception:
            pass

        # re-read env vars after attempted load
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')

    # Try MySQL first if credentials present
    if db_host and db_name and db_user and db_pass:
        try:
            conn = mysql.connector.connect(host=db_host, database=db_name, user=db_user, password=db_pass)
            return conn
        except mysql.connector.Error as e:
            print(f"Error de conexión a MySQL: {e}")
            # fallthrough to sqlite fallback

    # SQLite fallback (allows local testing without MySQL)
    try:
        db_file = os.path.join(BASE_DIR, 'gestor.sqlite3')
        sqlite_conn = sqlite3.connect(db_file, check_same_thread=False)
        sqlite_conn.row_factory = sqlite3.Row
        print(f"Usando fallback SQLite en {db_file}")
        return sqlite_conn
    except Exception as e:
        print(f"Error al crear/abrir la base SQLite: {e}")
        return None


def db_query(query, params=(), fetch=False):
    conn = get_db_connection()
    if not conn:
        return None
    result = None
    try:
        # SQLite branch
        if isinstance(conn, sqlite3.Connection):
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                rows = cursor.fetchall()
                # sqlite3.Row -> dict
                result = [dict(r) for r in rows]
            else:
                conn.commit()
                result = True
            cursor.close()
            conn.close()
            return result

        # MySQL branch (existing behavior)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = True
        except mysql.connector.Error as e:
            print(f"Error en la consulta a la base de datos: {e}")
            conn.rollback()
            result = False
        finally:
            cursor.close()
            conn.close()
        return result
    except Exception as e:
        print(f"Error en db_query: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False


def init_db():
    if not os.path.exists(EXCEL_FOLDER):
        os.makedirs(EXCEL_FOLDER)
    try:
        conn = get_db_connection()
        if not conn:
            print("ERROR al inicializar la BD: No se pudo establecer la conexión con la base de datos.")
            return

        default_username = 'Pauluk'
        default_password = 'Jap2005'
        proveedores_excel = ['BremenTools', 'Crossmaster', 'Berger', 'Chiesa', 'Cachan', 'Otros Proveedores']

        # SQLite initialization
        if isinstance(conn, sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute(''' CREATE TABLE IF NOT EXISTS stock ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                codigo TEXT, 
                nombre TEXT NOT NULL, 
                precio REAL NOT NULL, 
                cantidad INTEGER NOT NULL, 
                fecha_compra TEXT NOT NULL, 
                proveedor TEXT, 
                observaciones TEXT, 
                precio_texto TEXT, 
                avisar_bajo_stock INTEGER DEFAULT 0, 
                min_stock_aviso INTEGER DEFAULT NULL 
            ) ''')
            cursor.execute(''' CREATE TABLE IF NOT EXISTS proveedores_manual ( id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE ) ''')
            cursor.execute(''' CREATE TABLE IF NOT EXISTS productos_manual ( id INTEGER PRIMARY KEY AUTOINCREMENT, proveedor_id INTEGER, nombre TEXT NOT NULL, codigo TEXT, precio REAL NOT NULL, FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE ) ''')
            cursor.execute(''' CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL ) ''')

            cursor.execute("SELECT id FROM users WHERE username = ?", (default_username,))
            if cursor.fetchone() is None:
                hashed_password = generate_password_hash(default_password)
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (default_username, hashed_password))

            for nombre in proveedores_excel:
                cursor.execute("INSERT OR IGNORE INTO proveedores_manual (nombre) VALUES (?)", (nombre,))

            conn.commit()
            cursor.close()
            conn.close()
            print("Base de datos inicializada/verificada en SQLite con éxito.")
            return

        # MySQL initialization (existing)
        cursor = conn.cursor()
        cursor.execute(''' CREATE TABLE IF NOT EXISTS stock ( 
            id INT AUTO_INCREMENT PRIMARY KEY, 
            codigo TEXT, 
            nombre TEXT NOT NULL, 
            precio REAL NOT NULL, 
            cantidad INTEGER NOT NULL, 
            fecha_compra TEXT NOT NULL, 
            proveedor TEXT, 
            observaciones TEXT, 
            precio_texto TEXT, 
            avisar_bajo_stock TINYINT(1) DEFAULT 0, 
            min_stock_aviso INTEGER DEFAULT NULL 
        ) ''')
        # Asegurar que columnas nuevas existan en esquemas antiguos
        try:
            cursor.execute("ALTER TABLE stock ADD COLUMN IF NOT EXISTS avisar_bajo_stock TINYINT(1) DEFAULT 0")
        except Exception:
            try:
                cursor.execute("ALTER TABLE stock ADD COLUMN avisar_bajo_stock TINYINT(1) DEFAULT 0")
            except Exception:
                pass
        try:
            cursor.execute("ALTER TABLE stock ADD COLUMN IF NOT EXISTS min_stock_aviso INT DEFAULT NULL")
        except Exception:
            try:
                cursor.execute("ALTER TABLE stock ADD COLUMN min_stock_aviso INT DEFAULT NULL")
            except Exception:
                pass
        cursor.execute(''' CREATE TABLE IF NOT EXISTS proveedores_manual ( id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) NOT NULL UNIQUE ) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS productos_manual ( id INT AUTO_INCREMENT PRIMARY KEY, proveedor_id INT, nombre TEXT NOT NULL, codigo TEXT, precio REAL NOT NULL, FOREIGN KEY (proveedor_id) REFERENCES proveedores_manual(id) ON DELETE CASCADE ) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS users ( id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(80) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL ) ''')
        cursor.execute("SELECT id FROM users WHERE username = %s", (default_username,))
        if cursor.fetchone() is None:
            hashed_password = generate_password_hash(default_password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (default_username, hashed_password))
        for nombre in proveedores_excel:
            cursor.execute("INSERT IGNORE INTO proveedores_manual (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de datos inicializada/verificada en MySQL con éxito.")
    except Exception as e:
        print(f"\nERROR al inicializar la BD: {e}")

# --- Decorador de Autenticación ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de Autenticación ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_query("SELECT * FROM users WHERE username = %s", (username,), fetch=True)
        if user and check_password_hash(user[0]['password_hash'], password):
            session.clear()
            session.permanent = True
            session['user_id'] = user[0]['id']
            session['username'] = user[0]['username']
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))

# --- Rutas de la Aplicación Web (Protegidas) ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/historial')
@login_required
def historial():
    termino = request.args.get('q', '')
    if termino:
        like_pattern = f'%{termino}%'
        productos = db_query( "SELECT * FROM stock WHERE nombre LIKE %s OR codigo LIKE %s OR proveedor LIKE %s OR observaciones LIKE %s ORDER BY fecha_compra DESC, id DESC", (like_pattern, like_pattern, like_pattern, like_pattern), fetch=True )
    else:
        productos = db_query("SELECT * FROM stock ORDER BY fecha_compra DESC, id DESC", fetch=True)
    return render_template('historial.html', productos=productos, termino_busqueda=termino)

@app.route('/notificaciones')
@login_required
def notificaciones():
    notificaciones = session.get('notificaciones', [])
    return render_template('notificaciones.html', notificaciones=notificaciones)

@app.route('/borrar_notificacion/<int:idx>', methods=['POST'])
@login_required
def borrar_notificacion(idx):
    notificaciones = session.get('notificaciones', [])
    if 0 <= idx < len(notificaciones):
        notificaciones.pop(idx)
        session['notificaciones'] = notificaciones
    return redirect(url_for('notificaciones'))

@app.route('/borrar_todas_notificaciones', methods=['POST'])
@login_required
def borrar_todas_notificaciones():
    session['notificaciones'] = []
    return redirect(url_for('notificaciones'))

# --- Lógica para agregar notificación de stock bajo ---
def agregar_notificacion_stock_bajo(nombre, cantidad, min_stock):
    notificaciones = session.get('notificaciones', [])
    mensaje = f"El producto '{nombre}' tiene un stock bajo ({cantidad} unidades, mínimo configurado: {min_stock})."
    notificaciones.append({'mensaje': mensaje})
    session['notificaciones'] = notificaciones

@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    # --- Carrito en sesión ---
    if 'carrito' not in session:
        session['carrito'] = []
    carrito = session['carrito']

    if request.method == 'POST' and 'cargar_carrito' in request.form:
        # Cargar todos los productos del carrito al stock
        any_failed = False
        for item in carrito:
            # Persistir también las opciones de aviso de bajo stock si están presentes
            res = db_query(
                "INSERT INTO stock (codigo, nombre, precio, cantidad, fecha_compra, proveedor, observaciones, precio_texto, avisar_bajo_stock, min_stock_aviso) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    item.get('codigo'),
                    item['nombre'],
                    item['precio'],
                    item['cantidad'],
                    item['fecha_compra'],
                    item.get('proveedor'),
                    item.get('observaciones', ''),
                    item.get('precio_texto', ''),
                    int(item.get('avisar_bajo_stock', 0) or 0),
                    int(item.get('min_stock_aviso')) if item.get('min_stock_aviso') not in (None, '') else None
                )
            )
            if res is False or res is None:
                any_failed = True
                print(f"Fallo al insertar item en DB: {item}")
                flash(f"Error al insertar el producto '{item.get('nombre')}' en la base de datos.", 'danger')
        if not any_failed:
            session['carrito'] = []
            flash('Todos los productos del carrito fueron agregados al stock.', 'success')
        else:
            flash('Algunos productos NO se agregaron al stock. Revisa los registros del servidor.', 'warning')
        return redirect(url_for('agregar_producto'))

    if request.method == 'POST' and 'quitar_carrito' in request.form:
        idx = int(request.form.get('quitar_carrito'))
        if 0 <= idx < len(carrito):
            carrito.pop(idx)
            session['carrito'] = carrito
            flash('Producto quitado del carrito.', 'info')
        return redirect(url_for('agregar_producto'))

    if request.method == 'POST' and 'sumar_cantidad' in request.form:
        idx = int(request.form.get('sumar_cantidad'))
        if 0 <= idx < len(carrito):
            carrito[idx]['cantidad'] += 1
            session['carrito'] = carrito
        return redirect(url_for('agregar_producto'))

    if request.method == 'POST' and 'restar_cantidad' in request.form:
        idx = int(request.form.get('restar_cantidad'))
        if 0 <= idx < len(carrito):
            carrito[idx]['cantidad'] -= 1
            if carrito[idx]['cantidad'] <= 0:
                carrito.pop(idx)
            session['carrito'] = carrito
        return redirect(url_for('agregar_producto'))

    # Cambia: el formulario manual siempre agrega un nuevo ítem al carrito
    if request.method == 'POST' and 'agregar_carrito_manual' in request.form:
        codigo = request.form.get('codigo')
        nombre = request.form['nombre']
        precio_raw = request.form['precio']
        precio, precio_texto = parse_price(precio_raw)
        cantidad = int(request.form['cantidad'])
        fecha_compra = request.form['fecha_compra']
        proveedor = request.form.get('proveedor')
        observaciones = request.form.get('observaciones', '')
        avisar_bajo_stock = int(request.form.get('avisar_bajo_stock', 0))
        min_stock_aviso = request.form.get('min_stock_aviso')
        min_stock_aviso = int(min_stock_aviso) if min_stock_aviso else None
        carrito.append({
            'codigo': codigo,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad,
            'fecha_compra': fecha_compra,
            'proveedor': proveedor,
            'observaciones': observaciones,
            'precio_texto': precio_texto,
            'avisar_bajo_stock': avisar_bajo_stock,
            'min_stock_aviso': min_stock_aviso
        })
        session['carrito'] = carrito
        # Si se activa el aviso y la cantidad es baja, agregar notificación
        if avisar_bajo_stock and min_stock_aviso and cantidad <= min_stock_aviso:
            agregar_notificacion_stock_bajo(nombre, cantidad, min_stock_aviso)
        flash('Producto agregado al carrito.', 'success')
        return redirect(url_for('agregar_producto'))

    termino_excel = request.args.get('busqueda_excel', '')
    proveedor_excel_filtro = request.args.get('proveedor_excel', '')
    filtro_excel = request.args.get('filtro_excel', '')
    resultados_excel = []
    proveedores_excel_list = [ {'key': 'brementools', 'nombre': 'BremenTools'}, {'key': 'crossmaster', 'nombre': 'Crossmaster'}, {'key': 'berger', 'nombre': 'Berger'}, {'key': 'chiesa', 'nombre': 'Chiesa'}, {'key': 'cachan', 'nombre': 'Cachan'}, {'key': 'otros_proveedores', 'nombre': 'Otros Proveedores'} ]
    if termino_excel:
        resultados_excel = buscar_en_excel(termino_excel, proveedor_excel_filtro if proveedor_excel_filtro else None, filtro_excel if filtro_excel else None)
    proveedores_manual = db_query("SELECT * FROM proveedores_manual ORDER BY nombre", fetch=True)
    return render_template( 'agregar.html', resultados_excel=resultados_excel, termino_excel=termino_excel, proveedor_excel=proveedor_excel_filtro, filtro_excel=filtro_excel, proveedores_excel=proveedores_excel_list, proveedores_manual=proveedores_manual, fecha_actual=datetime.now().strftime('%Y-%m-%d'), carrito=carrito )

@app.route('/actualizar_stock/<int:id>', methods=['POST'])
@login_required
def actualizar_stock(id):
    try:
        cantidad_vendida = int(request.form['cantidad_vendida'])
        producto_actual_list = db_query("SELECT id, nombre, cantidad, avisar_bajo_stock, min_stock_aviso FROM stock WHERE id = %s", (id,), fetch=True)
        if not producto_actual_list:
            flash('El producto no existe.', 'danger')
            return redirect(url_for('historial'))
        producto_actual = producto_actual_list[0]
        if cantidad_vendida <= 0:
            flash('La cantidad vendida debe ser mayor que cero.', 'warning')
        elif cantidad_vendida > producto_actual['cantidad']:
            flash('No se puede vender más de la cantidad disponible en stock.', 'danger')
        else:
            nueva_cantidad = producto_actual['cantidad'] - cantidad_vendida
            if nueva_cantidad > 0:
                db_query("UPDATE stock SET cantidad = %s WHERE id = %s", (nueva_cantidad, id))
                flash('¡Vendido!', 'success')
                # Si el producto tiene aviso activado y la nueva cantidad es menor o igual al umbral, agregar notificación
                try:
                    avisar = bool(int(producto_actual.get('avisar_bajo_stock', 0) or 0))
                except Exception:
                    avisar = False
                min_aviso = producto_actual.get('min_stock_aviso')
                try:
                    if avisar and min_aviso is not None and int(min_aviso) >= 0 and nueva_cantidad <= int(min_aviso):
                        agregar_notificacion_stock_bajo(producto_actual.get('nombre', ''), nueva_cantidad, int(min_aviso))
                except Exception:
                    pass
            else:
                db_query("DELETE FROM stock WHERE id = %s", (id,))
                flash('¡Todo vendido!', 'warning')
                # Si fue eliminado y tenía aviso configurado, también puede ser interesante notificar que quedó en 0
                try:
                    avisar = bool(int(producto_actual.get('avisar_bajo_stock', 0) or 0))
                except Exception:
                    avisar = False
                min_aviso = producto_actual.get('min_stock_aviso')
                try:
                    if avisar and min_aviso is not None and int(min_aviso) >= 0 and 0 <= int(min_aviso):
                        agregar_notificacion_stock_bajo(producto_actual.get('nombre', ''), 0, int(min_aviso))
                except Exception:
                    pass
    except (ValueError, IndexError, TypeError):
        flash('Error al actualizar el stock. Verifique los datos.', 'danger')
    return redirect(url_for('historial'))

@app.route('/proveedores', methods=['GET'])
@login_required
def proveedores():
    proveedores_manual = db_query("SELECT * FROM proveedores_manual ORDER BY nombre", fetch=True)
    return render_template('proveedores.html', proveedores_manual=proveedores_manual)

@app.route('/agregar_proveedor_manual', methods=['POST'])
@login_required
def agregar_proveedor_manual():
    nombre = request.form.get('nombre')
    if nombre:
        db_query("INSERT IGNORE INTO proveedores_manual (nombre) VALUES (%s)", (nombre,))
        flash('Proveedor agregado exitosamente.', 'success')
    else:
        flash('El nombre del proveedor no puede estar vacío.', 'danger')
    return redirect(url_for('proveedores'))

@app.route('/eliminar_proveedor_manual/<int:id>', methods=['POST'])
@login_required
def eliminar_proveedor_manual(id):
    db_query("DELETE FROM proveedores_manual WHERE id = %s", (id,))
    flash('Proveedor eliminado exitosamente.', 'success')
    return redirect(url_for('proveedores'))

@app.route('/agregar_producto_manual', methods=['POST'])
@login_required
def agregar_producto_manual():
    proveedor_id = request.form['proveedor_id']
    nombre = request.form['nombre']
    codigo = request.form.get('codigo', '')
    precio_raw = request.form['precio']
    observaciones = request.form.get('observaciones', '')
    precio, precio_texto_error = parse_price(precio_raw)
    if precio_texto_error:
        flash('Formato de precio no válido.', 'danger')
        return redirect(url_for('agregar_producto'))
    proveedor_row = db_query("SELECT nombre FROM proveedores_manual WHERE id = %s", (proveedor_id,), fetch=True)
    proveedor_nombre = proveedor_row[0]['nombre'] if proveedor_row else ''
    try:
        df = pd.read_excel(MANUAL_PRODUCTS_FILE) if os.path.exists(MANUAL_PRODUCTS_FILE) else pd.DataFrame(columns=['Proveedor', 'Nombre', 'Codigo', 'Precio', 'Observaciones'])
        if 'Observaciones' not in df.columns: df['Observaciones'] = ''
        nuevo_producto = pd.DataFrame([{'Proveedor': proveedor_nombre, 'Nombre': nombre, 'Codigo': codigo, 'Precio': precio, 'Observaciones': observaciones}])
        df = pd.concat([df, nuevo_producto], ignore_index=True)
        df.to_excel(MANUAL_PRODUCTS_FILE, index=False)
        flash('Producto manual agregado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al guardar en Excel: {e}', 'danger')
    return redirect(url_for('agregar_producto'))

@app.route('/eliminar_producto_stock/<int:id>', methods=['POST'])
@login_required
def eliminar_producto_stock(id):
    db_query("DELETE FROM stock WHERE id = %s", (id,))
    flash('Producto quitado del historial de stock.', 'success')
    return redirect(url_for('historial'))

@app.route('/eliminar_manual', methods=['GET', 'POST'])
@login_required
def eliminar_manual():
    search_term = request.form.get('search_term', '')
    productos_encontrados = []

    if request.method == 'POST' and 'buscar' in request.form:
        if os.path.exists(MANUAL_PRODUCTS_FILE):
            try:
                df = pd.read_excel(MANUAL_PRODUCTS_FILE)
                df['Codigo'] = df['Codigo'].astype(str)
                df_filtrado = df[df['Nombre'].str.contains(search_term, case=False, na=False) | df['Codigo'].str.contains(search_term, case=False, na=False)]
                productos_encontrados = df_filtrado.to_dict('records')
            except Exception as e:
                flash(f"Error al leer el archivo Excel: {e}", 'danger')
        else:
            flash("El archivo de productos manuales no existe.", 'warning')

    elif request.method == 'POST' and 'eliminar' in request.form:
        codigo_a_eliminar = request.form.get('codigo_a_eliminar')
        if os.path.exists(MANUAL_PRODUCTS_FILE):
            try:
                df = pd.read_excel(MANUAL_PRODUCTS_FILE)
                df['Codigo'] = df['Codigo'].astype(str)
                df_original_len = len(df)
                df = df[df['Codigo'] != codigo_a_eliminar]
                if len(df) < df_original_len:
                    df.to_excel(MANUAL_PRODUCTS_FILE, index=False)
                    flash(f"Producto con código '{codigo_a_eliminar}' eliminado del archivo Excel.", 'success')
                else:
                    flash(f"No se encontró el producto con código '{codigo_a_eliminar}' para eliminar.", 'warning')
            except Exception as e:
                flash(f"Error al eliminar del archivo Excel: {e}", 'danger')
        return redirect(url_for('eliminar_manual'))

    return render_template('eliminar_manual.html', productos=productos_encontrados, search_term=search_term)

@app.route('/agregar_carrito_ajax', methods=['POST'])
@login_required
def agregar_carrito_ajax():
    if 'carrito' not in session:
        session['carrito'] = []
    carrito = session['carrito']
    data = request.get_json()
    codigo = data.get('codigo')
    nombre = data.get('nombre')
    precio_raw = data.get('precio')
    precio, precio_texto = parse_price(precio_raw)
    cantidad = int(data.get('cantidad', 1))
    fecha_compra = data.get('fecha_compra')
    proveedor = data.get('proveedor')
    observaciones = data.get('observaciones', '')
    avisar_bajo_stock = int(data.get('avisar_bajo_stock', 0) or 0)
    min_stock_aviso = data.get('min_stock_aviso')
    min_stock_aviso = int(min_stock_aviso) if min_stock_aviso not in (None, '') else None
    carrito.append({
        'codigo': codigo,
        'nombre': nombre,
        'precio': precio,
        'cantidad': cantidad,
        'fecha_compra': fecha_compra,
        'proveedor': proveedor,
        'observaciones': observaciones,
    'precio_texto': precio_texto,
    'avisar_bajo_stock': avisar_bajo_stock,
    'min_stock_aviso': min_stock_aviso
    })
    session['carrito'] = carrito
    # Renderizar solo la tabla del carrito como HTML para actualizarla por JS
    rendered_carrito = render_template('carrito_fragment.html', carrito=carrito)
    return jsonify({'success': True, 'html': rendered_carrito, 'msg': 'Producto agregado al carrito.'})

@app.route('/agregar_carrito_manual_ajax', methods=['POST'])
@login_required
def agregar_carrito_manual_ajax():
    if 'carrito' not in session:
        session['carrito'] = []
    carrito = session['carrito']
    data = request.get_json()
    codigo = data.get('codigo')
    nombre = data.get('nombre')
    precio_raw = data.get('precio')
    precio, precio_texto = parse_price(precio_raw)
    cantidad = int(data.get('cantidad', 1))
    fecha_compra = data.get('fecha_compra')
    proveedor = data.get('proveedor')
    observaciones = data.get('observaciones', '')
    avisar_bajo_stock = int(data.get('avisar_bajo_stock', 0) or 0)
    min_stock_aviso = data.get('min_stock_aviso')
    min_stock_aviso = int(min_stock_aviso) if min_stock_aviso not in (None, '') else None
    carrito.append({
        'codigo': codigo,
        'nombre': nombre,
        'precio': precio,
        'cantidad': cantidad,
        'fecha_compra': fecha_compra,
        'proveedor': proveedor,
        'observaciones': observaciones,
    'precio_texto': precio_texto,
    'avisar_bajo_stock': avisar_bajo_stock,
    'min_stock_aviso': min_stock_aviso
    })
    session['carrito'] = carrito
    rendered_carrito = render_template('carrito_fragment.html', carrito=carrito)
    return jsonify({'success': True, 'html': rendered_carrito, 'msg': 'Producto agregado al carrito.'})

@app.route('/carrito_accion', methods=['POST'])
@login_required
def carrito_accion():
    if 'carrito' not in session:
        session['carrito'] = []
    carrito = session['carrito']
    data = request.get_json()
    accion = data.get('accion')
    idx = int(data.get('idx', -1))
    cantidad = int(data.get('cantidad', 1))
    changed = False
    if 0 <= idx < len(carrito):
        if accion == 'sumar':
            carrito[idx]['cantidad'] += 1
            changed = True
        elif accion == 'restar':
            carrito[idx]['cantidad'] -= 1
            if carrito[idx]['cantidad'] <= 0:
                carrito.pop(idx)
            changed = True
        elif accion == 'actualizar':
            if cantidad > 0:
                carrito[idx]['cantidad'] = cantidad
            else:
                carrito.pop(idx)
            changed = True
        elif accion == 'eliminar':
            carrito.pop(idx)
            changed = True
    if changed:
        session['carrito'] = carrito
    rendered_carrito = render_template('carrito_fragment.html', carrito=carrito)
    return jsonify({'success': True, 'html': rendered_carrito})

# --- Bloque de inicialización de la BD ---
with app.app_context():
    init_db()

# --- Funciones de Lógica de Negocio ---
def buscar_en_excel(termino_busqueda, proveedor_filtro=None, filtro_adicional=None):
    PROVEEDOR_CONFIG = {
        'brementools': { 'fila_encabezado': 5, 'codigo': ['codigo', 'Código', 'CODIGO'], 'producto': ['producto', 'Producto', 'PRODUCTO'], },
        'crossmaster': { 'fila_encabezado': 11, 'codigo': ['codigo', 'Codigo', 'CODIGO'], 'producto': ['descripcion', 'Descripcion', 'DESCRIPCION'], },
        'berger': { 'fila_encabezado': 0, 'codigo': ['cod', 'COD', 'codigo', 'Codigo'], 'producto': ['detalle', 'DETALLE', 'producto', 'Producto'], 'precio': ['P.VENTA'], },
        'chiesa': { 'fila_encabezado': 1, 'codigo': ['codigo', 'Codigo', 'CODIGO'], 'producto': ['descripción', 'Descripción', 'descripcion', 'Descripcion'], },
        'cachan': { 'fila_encabezado': 0, 'codigo': ['codigo', 'Codigo', 'CODIGO'], 'producto': ['nombre', 'Nombre', 'NOMBRE'], },
        'otros_proveedores': { 'archivo_excel': MANUAL_PRODUCTS_FILE, 'codigo': ['Codigo'], 'producto': ['Nombre'], 'proveedor': ['Proveedor'], 'precio': ['Precio'] }
    }
    resultados = []
    archivos_a_buscar = []
    if proveedor_filtro:
        if proveedor_filtro in PROVEEDOR_CONFIG:
            config = PROVEEDOR_CONFIG[proveedor_filtro]
            if 'archivo_excel' in config:
                if os.path.exists(config['archivo_excel']):
                    archivos_a_buscar.append(config['archivo_excel'])
            else:
                # Buscar archivos insensible a mayúsculas/minúsculas
                all_files = glob.glob(os.path.join(EXCEL_FOLDER, '*.xlsx'))
                archivos_a_buscar = [f for f in all_files if proveedor_filtro.lower() in os.path.basename(f).lower()]
                print(f"Archivos encontrados para proveedor '{proveedor_filtro}': {archivos_a_buscar}")
    else:
        archivos_a_buscar = glob.glob(os.path.join(EXCEL_FOLDER, '*.xlsx'))
        print(f"Archivos encontrados para todos los proveedores: {archivos_a_buscar}")

    for archivo in archivos_a_buscar:
        try:
            nombre_archivo = os.path.basename(archivo).lower()
            proveedor_key = None
            for key, config in PROVEEDOR_CONFIG.items():
                if 'archivo_excel' in config and os.path.exists(config['archivo_excel']) and os.path.samefile(archivo, config['archivo_excel']):
                    proveedor_key = key
                    break
                elif 'archivo_excel' not in config and key in nombre_archivo:
                    proveedor_key = key
                    break
            if not proveedor_key:
                print(f"Archivo {archivo} no coincide con ningún proveedor_key")
                continue
            config = PROVEEDOR_CONFIG[proveedor_key]
            fila_encabezado = config.get('fila_encabezado', 0)
            try:
                df = pd.read_excel(archivo, header=fila_encabezado)
                df.columns = [str(col).strip() for col in df.columns]
            except Exception:
                df_tmp = pd.read_excel(archivo, header=None)
                for idx in range(min(15, len(df_tmp))):
                    row = df_tmp.iloc[idx].astype(str)
                    if any('codigo' in val.lower() for val in row) or any('producto' in val.lower() for val in row) or any('descripcion' in val.lower() for val in row):
                        fila_encabezado = idx
                        break
                df = pd.read_excel(archivo, header=fila_encabezado)
                df.columns = [str(col).strip() for col in df.columns]
            col_codigo = next((alias for alias in config['codigo'] if alias in df.columns), None)
            col_producto = next((alias for alias in config['producto'] if alias in df.columns), None)
            col_proveedor = next((alias for alias in config.get('proveedor', []) if alias in df.columns), None)
            col_precio = next((alias for alias in config.get('precio', []) if alias in df.columns), None)
            if not col_codigo or not col_producto:
                print(f"Archivo {archivo} no tiene columnas requeridas: codigo={col_codigo}, producto={col_producto}")
                continue
            df_filtrado = df[df[col_producto].astype(str).str.contains(termino_busqueda, case=False, na=False) | df[col_codigo].astype(str).str.contains(termino_busqueda, case=False, na=False)].copy()
            # Aplicar filtro adicional si corresponde
            if filtro_adicional:
                filtro_lower = filtro_adicional.lower()
                df_filtrado = df_filtrado[df_filtrado.apply(lambda r: filtro_lower in str(r.get(col_producto, '')).lower() or filtro_lower in str(r.get(col_codigo, '')).lower(), axis=1)]
            for _, row in df_filtrado.iterrows():
                precio_num, precio_texto = 0.0, ''
                if col_precio and pd.notna(row.get(col_precio)):
                    precio_num, precio_texto = parse_price(str(row[col_precio]))
                resultados.append({
                    'codigo': row[col_codigo],
                    'nombre': row[col_producto],
                    'proveedor': row.get(col_proveedor) or proveedor_key.capitalize(),
                    'precio': precio_num,
                    'precio_texto': precio_texto,
                    'Observaciones': row.get('Observaciones', '')
                })
        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")
    print(f"Resultados encontrados: {len(resultados)}")
    return resultados

@app.route('/agregar_proveedor_manual_ajax', methods=['POST'])
@login_required
def agregar_proveedor_manual_ajax():
    nombre = request.get_json().get('nombre')
    if nombre:
        db_query("INSERT IGNORE INTO proveedores_manual (nombre) VALUES (%s)", (nombre,))
        proveedores_manual = db_query("SELECT * FROM proveedores_manual ORDER BY nombre", fetch=True)
        proveedores_list = []
        for p in proveedores_manual:
            proveedores_list.append({'id': p['id'], 'nombre': p['nombre']})
        return jsonify({'success': True, 'proveedores': proveedores_list})
    else:
        return jsonify({'success': False, 'msg': 'El nombre del proveedor no puede estar vacío.'})

@app.route('/eliminar_seleccionados', methods=['POST'])
@login_required
def eliminar_seleccionados():
    ids = request.form.getlist('seleccionados')
    if ids:
        for id in ids:
            db_query("DELETE FROM stock WHERE id = %s", (id,))
        flash(f"{len(ids)} productos eliminados del historial.", 'success')
    else:
        flash('No se seleccionaron productos para eliminar.', 'warning')
    return redirect(url_for('historial'))

@app.route('/eliminar_todo_historial', methods=['POST'])
@login_required
def eliminar_todo_historial():
    db_query("DELETE FROM stock")
    flash('Todos los productos han sido eliminados del historial.', 'success')
    return redirect(url_for('historial'))

# Exponer la aplicación para WSGI (PythonAnywhere)
application = app

if __name__ == "__main__":
    app.run(debug=True)
