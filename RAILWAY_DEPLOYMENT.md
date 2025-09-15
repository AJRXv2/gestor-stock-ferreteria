# Guía de Despliegue en Railway

Esta guía contiene los pasos necesarios para desplegar correctamente la aplicación Gestor de Stock en Railway y asegurar que la base de datos PostgreSQL esté correctamente configurada.

## Prerrequisitos

- Cuenta en [Railway](https://railway.app/)
- Repositorio en GitHub con el código del Gestor de Stock
- Git instalado en tu máquina local

## Pasos para el Despliegue

### 1. Preparar el Código (Ya Completado)

✅ El código ya ha sido adaptado para PostgreSQL.  
✅ El archivo `requirements.txt` incluye todas las dependencias necesarias.  
✅ El archivo `Procfile` está configurado correctamente.  
✅ Se ha implementado el endpoint de migración `/api/fix_railway_db`.

### 2. Conectar Railway con GitHub

1. Inicia sesión en [Railway Dashboard](https://railway.app/dashboard)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Si es la primera vez, conecta tu cuenta de GitHub:
   - Haz clic en "Connect GitHub"
   - Autoriza a Railway para acceder a tus repositorios
5. Busca y selecciona el repositorio `gestor-stock-ferreteria`
6. Haz clic en "Deploy Now"

### 3. Agregar Base de Datos PostgreSQL

1. En el panel del proyecto recién creado, haz clic en "New"
2. Selecciona "Database" y luego "PostgreSQL"
3. Espera a que se aprovisione la base de datos (esto puede tardar unos minutos)

### 4. Configurar Variables de Entorno

1. En el panel del proyecto, haz clic en el servicio web (no en la base de datos)
2. Ve a la pestaña "Variables"
3. Asegúrate de que `DATABASE_URL` ya está configurada (Railway lo hace automáticamente)
4. Agrega las siguientes variables:
   - `MIGRATION_TOKEN`: Genera un token seguro (por ejemplo, usando [este generador](https://generate-random.org/api-token-generator))
   - `PORT`: 8080 (el puerto que Railway espera)
   - `FLASK_ENV`: production
   - `SECRET_KEY`: Genera una clave secreta para Flask (distinta del token de migración)

### 5. Ejecutar la Migración de la Base de Datos

Después de que el despliegue esté completo:

1. Obtén la URL de tu aplicación desde el panel de Railway (algo como `https://gestor-stock-ferreteria-xxxx.up.railway.app`)
2. Ejecuta el siguiente comando desde tu máquina local (reemplaza los valores según corresponda):

```bash
curl -X POST https://gestor-stock-ferreteria-xxxx.up.railway.app/api/fix_railway_db -H "X-Migration-Token: TU_TOKEN_AQUI"
```

Alternativamente, puedes usar Postman o cualquier otra herramienta para hacer una petición POST al endpoint con el header `X-Migration-Token` configurado.

### 6. Verificar la Migración

1. La respuesta del endpoint debe ser un JSON con `"success": true` si la migración fue exitosa
2. Si hay algún error, revisa los logs de la aplicación en Railway:
   - Ve al panel del proyecto
   - Selecciona el servicio web
   - Ve a la pestaña "Logs"

## Solución de Problemas

### La Aplicación no Funciona Después de la Migración

Si la aplicación sigue teniendo problemas después de la migración:

1. Verifica los logs en Railway para identificar errores específicos
2. Considera hacer cambios locales, probarlos, y luego hacer un nuevo despliegue:
   - Modifica el código según sea necesario
   - Haz commit y push a GitHub
   - Railway detectará los cambios y hará un nuevo despliegue automáticamente

### Errores en la Base de Datos

Si encuentras errores específicos de la base de datos:

1. En Railway, haz clic en el servicio de PostgreSQL
2. Ve a la pestaña "Data"
3. Puedes ejecutar consultas SQL directamente para verificar y modificar la estructura de la base de datos

## Comandos Útiles

### Probar el Endpoint de Migración Localmente

```bash
# Configura el token de migración
$env:MIGRATION_TOKEN = "tu_token_secreto"

# Ejecuta el script de prueba
python test_migration_endpoint.py
```

### Ejecutar Consultas SQL en Railway

1. Ve al servicio de PostgreSQL en Railway
2. Selecciona la pestaña "Data"
3. Ejecuta consultas como:

```sql
-- Ver todas las tablas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Verificar estructura de una tabla específica
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'proveedores_duenos';
```

## Contacto y Soporte

Si encuentras problemas durante el despliegue, puedes:

1. Revisar los logs en Railway para obtener más información sobre los errores
2. Consultar la [documentación de Railway](https://docs.railway.app/)
3. Contactar al desarrollador para soporte adicional