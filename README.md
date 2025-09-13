# Gestor de Stock - Ferretería

Sistema de gestión de inventario para ferretería con soporte para múltiples propietarios.

## 🚀 Despliegue en Railway

### Paso 1: Crear cuenta en Railway
1. Ve a [railway.app](https://railway.app)
2. Regístrate con GitHub
3. Conecta tu repositorio

### Paso 2: Configurar variables de entorno
En Railway, ve a tu proyecto y configura estas variables:

```
SECRET_KEY=tu_secret_key_muy_seguro_aqui
DATABASE_URL=postgresql://usuario:password@host:puerto/database
```

### Paso 3: Desplegar
Railway detectará automáticamente que es una aplicación Python y usará el `Procfile`.

## 🛠️ Desarrollo Local

### Instalación
```bash
pip install -r requirements.txt
```

### Configuración
1. Copia `.env.example` a `.env`
2. Configura las variables de entorno
3. Ejecuta: `python gestor.py`

### Inicialización de Base de Datos
El proyecto puede usar SQLite (local) o PostgreSQL (producción). Las tablas se crean automáticamente con `init_db()` interno, pero ahora disponés de un script dedicado:

```bash
python init_db.py            # Crea tablas (usa DATABASE_URL si está definida, sino SQLite)
FORCE_RESET=1 python init_db.py  # Elimina y recrea tablas (cuidado: borra datos)
```

Variables útiles:
```
DATABASE_URL=postgresql://usuario:pass@host:puerto/dbname
AUTO_INIT_DB=1   # Si la definís al arrancar gestor.py intentará ejecutar init_db.py automáticamente
```

Credenciales iniciales (solo si no existe usuario):
```
usuario: admin
password: admin
```
Cambialas inmediatamente en producción.

## 📦 Migraciones de Base de Datos

Ahora el proyecto incluye un sistema simple de migraciones versionadas.

Estructura:
```
migrations/
  001_baseline.sql
  002_example_add_column.sql   (ejemplo, comentado)
```
Cada archivo debe seguir el patrón: `NNN_descripcion.sql` donde `NNN` es un número incremental con 3 dígitos.

Tabla de control: `schema_migrations` (se crea automáticamente si no existe).

### Comandos

```bash
python migrate.py status      # Ver migraciones aplicadas / pendientes
python migrate.py apply       # Aplicar todas las migraciones pendientes
python migrate.py apply 002   # Aplicar solo la versión 002
python migrate.py mark_all    # Marca todas como aplicadas (sin ejecutar) ⚠️
```

### Flujo recomendado para cambio de esquema
1. Crear un nuevo archivo en `migrations/` con el siguiente número libre (ej: `003_agregar_indice_stock.sql`).
2. Escribir SQL idempotente (usar `IF NOT EXISTS`, verificar existencia de columnas en SQLite cuando aplique).
3. Probar localmente: `python migrate.py status` → `python migrate.py apply`.
4. Subir commit y desplegar. En producción ejecutar el mismo comando (`apply`).
5. Verificar integridad con la app (logs y endpoints de debug si existen).

### Buenas prácticas
- Evitá modificar archivos ya aplicados (creá una nueva migración en su lugar).
- Si cometiste un error en una migración ya aplicada, crea una nueva que lo corrija.
- No uses `FORCE_RESET` en producción salvo casos excepcionales (y con backup previo).
- Respaldá la base de datos antes de cambios estructurales importantes.

### Diferencias entre SQLite y PostgreSQL
- PostgreSQL soporta `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
- SQLite no soporta (en versiones clásicas) `IF NOT EXISTS` para columnas: puedes simular verificación consultando `PRAGMA table_info(tabla)` antes de alterar (en migraciones más avanzadas podrías usar un script Python en lugar de SQL puro si lo necesitás).

### Migración inicial existente
`001_baseline.sql` incluye la creación de todas las tablas actuales y la tabla `schema_migrations`. Si ya tenías datos previos, ejecutá:
```
python migrate.py mark_all
```
para marcarla como aplicada y evitar que intente crear lo que ya existe.

## 📊 Características

- ✅ Gestión de stock por propietario (Ferretería General / Ricky)
- ✅ Búsqueda en listas de precios Excel
- ✅ Productos manuales
- ✅ Notificaciones de stock bajo
- ✅ Historial de ventas
- ✅ Carrito de compras
- ✅ Base de datos PostgreSQL (producción) / SQLite (desarrollo)
- ✅ Importación de facturas PDF (experimental) para cargar productos automáticamente al carrito
- ✅ Script de inicialización de esquema (`init_db.py`) y auto-init opcional (AUTO_INIT_DB=1)
- ✅ Sistema de migraciones (001 baseline + 003 índices de rendimiento)
- ✅ Control de stock bajo (columns avisar_bajo_stock / min_stock_aviso vía migración 004)

## 🔧 Tecnologías

- **Backend**: Flask, Python 3.13
- **Base de datos**: PostgreSQL (Railway) / SQLite (local)
- **Frontend**: Bootstrap, JavaScript
- **Archivos**: Excel (openpyxl, pandas)
- **PDF**: pdfplumber (extracción de texto de facturas)

## 🧪 Importar Factura PDF (Beta)

En el menú "Importar Factura PDF" podés subir una factura en formato PDF. El sistema intentará detectar líneas con el patrón de items (cantidad, código, descripción, precio unitario) y los agrega al carrito para revisión antes de cargar al stock.

Limitaciones iniciales:
- Heurístico, puede omitir o interpretar mal algunas líneas.
- Solo extrae cantidad, código, descripción y precio unitario (sin IVA separado).
- Si el PDF es una imagen escaneada sin texto embebido no funcionará (no hay OCR todavía).

Si no detecta ningún producto revisá que el PDF tenga texto seleccionable. Para mejoras se podría integrar OCR (pytesseract) en el futuro.
