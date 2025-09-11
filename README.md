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

## 📊 Características

- ✅ Gestión de stock por propietario (Ferretería General / Ricky)
- ✅ Búsqueda en listas de precios Excel
- ✅ Productos manuales
- ✅ Notificaciones de stock bajo
- ✅ Historial de ventas
- ✅ Carrito de compras
- ✅ Base de datos PostgreSQL (producción) / SQLite (desarrollo)

## 🔧 Tecnologías

- **Backend**: Flask, Python 3.13
- **Base de datos**: PostgreSQL (Railway) / SQLite (local)
- **Frontend**: Bootstrap, JavaScript
- **Archivos**: Excel (openpyxl, pandas)
